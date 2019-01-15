import subprocess
import datetime
import os
import sys
import numpy as np
import math as m
import cmath as cm
import pya
from SiEPIC.ann import qopticParser1 as qp
from enum import Enum
import skrf as rf
import scipy.io as sio
from scipy import signal as sig
from SiEPIC.ann import waveguideNN as wn
from scipy.interpolate import splev, splrep, interp1d

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "NN_SiO2_neff.h5")
model = wn.loadWaveguideNN(path)

def strToSci(str):
    ex = str[-1]
    base = float(str[:-1])
    if(ex == 'm'):
        return base * 1e-3
    elif(ex == 'u'):
        return base * 1e-6
    elif(ex == 'n'):
        return base * 1e-9
    else:
        return float(str(base) + ex)

def findPortMatch(name, listofcells):
    cella = cellb = inda = indb = -1
    found = False
    for d in range(0, len(listofcells)):
        for p in range(0, len(listofcells[d].p)):
            if(listofcells[d].p[p] == name):
                cella = d
                inda = p
                found = True
                break
        if found:
            break
    found = False
    for d in range(cella+1, len(listofcells)):
        for p in range(0, len(listofcells[d].p)):
            if(listofcells[d].p[p] == name):
                cellb = d
                indb = p
                found = True
                break
        if found:
            break
    if(cellb == -1):
        for p in range(inda+1, len(listofcells[cella].p)):
            if(listofcells[cella].p[p] == name):
                cellb = cella
                indb = p
                break
    return [cella, inda, cellb, indb]

class DEVTYPE(Enum):
    BDC = 'ebeam_bdc_te1550'
    DC = 'ebeam_dc_halfring_te1550'
    GC = 'ebeam_gc_te1550'
    YB = 'ebeam_y_1550'

class Cell():
    def __init__(self, id):
        self.deviceID = id
        self.devType = None
        self.p = []
        self.iswg = False
        self.wglen = None
        self.wgwid = None
        self.s = None
        self.f = []

    def readSparamFile(self):
        isgc = False
        if(self.devType == DEVTYPE.BDC.value):
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/EBeam_1550_TE_BDC.sparam")
        elif self.devType == DEVTYPE.DC.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/te_ebeam_dc_halfring_straight_gap=30nm_radius=3um_width=520nm_thickness=210nm_CoupleLength=0um.dat")
        elif self.devType == DEVTYPE.GC.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/GC_TE1550_thickness=220 deltaw=0.txt")
            isgc = True
        elif self.devType == DEVTYPE.YB.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/Ybranch_Thickness =220 width=500.sparam")
        else:
            print("ERROR: Unknown Device Type")
            return
        #if(self.devType != DEVTYPE.GC.value): #figure out how to parse GC devices
        s, f = pya.Cell.Reader.readSparamData(filename, len(self.p), isgc)
        self.f = np.linspace(f[0], f[-1], 1000)
        func = interp1d(f, s, kind='cubic', axis=0)
        self.s = func(self.f)            

    def wgSparam(self):        
        c0 = 299792458 #m/s
        mat = np.zeros((len(self.f),2,2), dtype=complex)
        width = 0.5 #um
        thickness = 0.22 #um
        mode = 0 #TE
        alpha = 0 #assuming lossless waveguide
        wl = np.true_divide(c0,self.f)
        neff = wn.getWaveguideIndex(model,np.transpose(wl),width,thickness,mode)
        K = alpha + (2*m.pi*np.true_divide(neff,wl))*1j
        for x in range(0, len(neff)):
          mat[x,0,1] = mat[x,1,0] = cm.exp(-K[x] * complex(self.wglen))
        self.s = mat        

    def printPorts(self):
        print("DEVICE ID:", self.deviceID, "has", len(self.p), "port(s).")
        print(self.p)
        #for port in self.p:
        #    print(port)
        #if self.iswg:

        #else:
        #    print("DEVICE %d TYPE: %s" % (self.deviceID, self.devType))
        #    if(self.devType != DEVTYPE.GC.value):
        #        print(self.s[0])


class Parser:
    def __init__(self, filepath):
        self.cellList = []
        self.nextID = 0
        self.filepath = filepath
        self.nports = 0

    def createCell(self):
        pass

    def parseFile(self):
        infile = open(self.filepath)
        filelines = infile.readlines()
        for line in filelines:
            elements = line.split()
            if len(elements) > 0:
                if (".ends" in elements[0]):
                    break
                elif ("." in elements[0]) or ("*" in elements[0]):
                    continue
                else:
                    self.parseCell(elements)
        
    def parseCell(self, line):
        newCell = Cell(self.nextID)
        self.nextID += 1
        for devtype in DEVTYPE:
            if devtype.value in line[0]:
                newCell.devType = devtype.value
        for item in line:
            if "N$" in item:
                port = str(item).replace("N$", '')
                newCell.p.append(port)
                if int(port) > self.nports:
                    self.nports = int(port)
            if "ebeam_wg" in item:
                newCell.iswg = True
            if "wg_length=" in item:
                wglen = str(item).replace("wg_length=", '')
                newCell.wglen = strToSci(wglen)
            if "wg_width=" in item:
                wgwid = str(item).replace("wg_width=", '')
                newCell.wgwid = strToSci(wgwid)
        if not newCell.iswg:
            newCell.readSparamFile()
        else:
            #get f from another cell and do math for s
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/Ybranch_Thickness =220 width=500.sparam")
            _, f = pya.Cell.Reader.readSparamData(filename, 3, False)
            newCell.f = np.linspace(f[0], f[-1], 1000)
            newCell.wgSparam()
        self.cellList.append(newCell)

    def cascadeCells(self):
        #loop through ports in cells and use skrf.connect_s or skrf.innerconnect_s
        #until only one cell is left
        if self.nports == 0:
            return
        for n in range(0, self.nports + 1):
            ca, ia, cb, ib = findPortMatch(str(n), self.cellList)
            if ca == cb:
                self.cellList[ca].s = rf.innerconnect_s(self.cellList[ca].s, ia, ib)
                del self.cellList[ca].p[ia]
                if ia < ib:
                    del self.cellList[ca].p[ib-1]
                else:
                    del self.cellList[ca].p[ib]
            else:
                d = Cell(self.nextID)
                d.f = self.cellList[0].f
                self.nextID += 1
                d.s = rf.connect_s(self.cellList[ca].s, ia, self.cellList[cb].s, ib)
                del self.cellList[ca].p[ia]
                del self.cellList[cb].p[ib]
                d.p = self.cellList[ca].p + self.cellList[cb].p
                del self.cellList[ca]
                if ca < cb:
                    del self.cellList[cb-1]
                else:
                    del self.cellList[cb]
                self.cellList.append(d)


    def getCells(self):
        return self.cellList

    def getCellCount(self):
        return len(self.cellList)


class Params:
    def get_sparameters(filename):
        test = Parser(filename)
        test.parseFile()
        test.cascadeCells()
        mat = test.cellList[0].s
        freq = test.cellList[0].f
        return (mat, freq)
    
pya.Cell.Params = Params

