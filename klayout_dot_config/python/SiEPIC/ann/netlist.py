####################################################
#
#   FORMERLY qopticParser1.py FUNCTIONS BELOW
#
####################################################

import pya
import numpy as np
import cmath as cm

class Reader:
    '''
    class to extend the pya.Cell class with the functionality to read/parse 
    files containing s-parameter data for photonic components
    '''

    def readSparamData(filename, numports, isgc):
        '''
        Function that takes a file containing s-parameters, parses it, and 
        returns an array of frequency values and a 3D matrix of s-parameters
        Args:
            filename (str): name of file to be parsed
            numports (int): the number of ports the photonic component has
            isgc (boolean): flag indicating the component is a grating coupler
                            grating couplers are a special case
        Returns:
            S (3D list of complex-128): S-matrix for the component associated with the file
            F (list of float): Frequency array for the component associated with the file
        '''

        F = []
        S = []
        fid = open(filename, "r")
        
        if isgc is True:
            '''
            grating couplers have a different file format from the other component types
            so a special case is required to parse them
            '''

            #grating coupler compact models have 100 points for each s-matrix index
            arrlen = 100
            
            lines = fid.readlines()
            F = np.zeros(arrlen)
            S = np.zeros((arrlen,2,2), 'complex128')
            for i in range(0, arrlen):
                words = lines[i].split()
                F[i] = float(words[0])
                S[i,0,0] = cm.rect(float(words[1]), float(words[2]))
                S[i,0,1] = cm.rect(float(words[3]), float(words[4]))
                S[i,1,0] = cm.rect(float(words[5]), float(words[6]))
                S[i,1,1] = cm.rect(float(words[7]), float(words[8]))
            F = F[::-1]
            S = S[::-1,:,:]
        
        else:
            '''
            Common case
            Parsing a '.sparam' file
            '''

            line = fid.readline()
            line = fid.readline()
            numrows = int(tuple(line[1:-2].split(','))[0])
            S = np.zeros((numrows, numports, numports), dtype='complex128')
            r = m = n = 0
            for line in fid:
                if(line[0] == '('):
                    continue
                data = line.split()
                data = list(map(float, data))
                if(m == 0 and n == 0):
                    F.append(data[0])
                S[r,m,n] = data[1] * np.exp(1j*data[2])
                r += 1
                if(r == numrows):
                    r = 0
                    m += 1
                    if(m == numports):
                        m = 0
                        n += 1
                        if(n == numports):
                            break
        fid.close()
        return [S, F]
        
#extending the pya.Cell class
pya.Cell.Reader = Reader

####################################################
#
#   FORMERLY export_netlist.py FUNCTIONS BELOW
#
####################################################

import pya
import SiEPIC.extend as se
import SiEPIC.core as cor

def spice_netlist_export(self, verbose=False, opt_in_selection_text=[]):
    '''
    This function gathers information from the current top cell in Klayout into a netlist
    for a photonic circuit. This netlist is used in simulations.

    Most of this function comes from a function in 'lukasc-ubc/SiEPIC-Tools/klayout_dot_config/python/SiEPIC/extend.py' which does the
    same thing. This function has parts of that one removed because they were not needed for our toolbox.
    '''

    import SiEPIC
    from SiEPIC import _globals
    from time import strftime
    from SiEPIC.utils import eng_str

    from SiEPIC.utils import get_technology
    TECHNOLOGY = get_technology()
    if not TECHNOLOGY['technology_name']:
        v = pya.MessageBox.warning("Errors", "SiEPIC-Tools requires a technology to be chosen.  \n\nThe active technology is displayed on the bottom-left of the KLayout window, next to the T. \n\nChange the technology using KLayout File | Layout Properties, then choose Technology and find the correct one (e.g., EBeam, GSiP).", pya.MessageBox.Ok)
        return 'x', 'x', 0, [0]
    # get the netlist from the entire layout
    nets, components = self.identify_nets()

    if not components:
        v = pya.MessageBox.warning("Errors", "No components found.", pya.MessageBox.Ok)
        return 'no', 'components', 0, ['found']

    if verbose:
        print("* Display list of components:")
        [c.display() for c in components]
        print("* Display list of nets:")
        [n.display() for n in nets]

    text_main = '* Spice output from KLayout SiEPIC-Tools v%s, %s.\n\n' % (
        SiEPIC.__version__, strftime("%Y-%m-%d %H:%M:%S"))
    text_subckt = text_main
        
    circuit_name = self.name.replace('.', '')  # remove "."
    if '_' in circuit_name[0]:
        circuit_name = ''.join(circuit_name.split('_', 1))  # remove leading _

    KLayoutInterconnectRotFlip = \
    {(0, False): [0, False],
    (90, False): [270, False],
    (180, False): [180, False],
    (270, False): [90, False],
    (0, True): [180, True],
    (90, True): [90, True],
    (180, True): [0, True],
    (270, True): [270, False]}

    # create the top subckt:
    #text_subckt += '.subckt %s%s%s\n' % (circuit_name, electricalIO_pins, opticalIO_pins)
    # assign MC settings before importing netlist components
    text_subckt += '.param MC_uniformity_width=0 \n'
    text_subckt += '.param MC_uniformity_thickness=0 \n'
    text_subckt += '.param MC_resolution_x=100 \n'
    text_subckt += '.param MC_resolution_y=100 \n'
    text_subckt += '.param MC_grid=10e-6 \n'
    text_subckt += '.param MC_non_uniform=99 \n'

    ioports = -1
    for c in components:
        # optical nets: must be ordered electrical, optical IO, then optical
        nets_str = ''
        for p in c.pins:
            if p.type == _globals.PIN_TYPES.ELECTRICAL:
                nets_str += " " + c.component + '_' + str(c.idx) + '_' + p.pin_name
        for p in c.pins:
            if p.type == _globals.PIN_TYPES.OPTICALIO:
                nets_str += " N$" + str(ioports)
                ioports -= 1
        #pinIOtype = any([p for p in c.pins if p.type == _globals.PIN_TYPES.OPTICALIO])
        for p in c.pins:
            if p.type == _globals.PIN_TYPES.OPTICAL:
                if p.net.idx != None:
                    nets_str += " N$" + str(p.net.idx)
                #if p.net.idx != None:
                #    nets_str += " N$" + str(p.net.idx)
                else:
                    nets_str += " N$" + str(ioports)
                    ioports -= 1

        trans = KLayoutInterconnectRotFlip[(c.trans.angle, c.trans.is_mirror())]

        flip = ' sch_f=true' if trans[1] else ''
        if trans[0] > 0:
            rotate = ' sch_r=%s' % str(trans[0])
        else:
            rotate = ''

        # Check to see if this component is an Optical IO type.
        pinIOtype = any([p for p in c.pins if p.type == _globals.PIN_TYPES.OPTICALIO])

        ignoreOpticalIOs = False
        if ignoreOpticalIOs and pinIOtype:
            # Replace the Grating Coupler or Edge Coupler with a 0-length waveguide.
            component1 = "ebeam_wg_strip_1550"
            params1 = "wg_length=0u wg_width=0.500u"
        else:
            component1 = c.component
            params1 = c.params

        text_subckt += ' %s %s %s ' % (component1.replace(' ', '_') +
                                       "_" + str(c.idx), nets_str, component1.replace(' ', '_'))
        if c.library != None:
            text_subckt += 'library="%s" ' % c.library
        x, y = c.Dcenter.x, c.Dcenter.y
        text_subckt += '%s lay_x=%s lay_y=%s\n' % \
            (params1, eng_str(x * 1e-6), eng_str(y * 1e-6))

    text_subckt += '.ends %s\n\n' % (circuit_name)
    return text_subckt, text_main

pya.Cell.spice_netlist_export_ann = spice_netlist_export


####################################################
#
#   FORMERLY cascade_netlist.py FUNCTIONS BELOW
#
####################################################

# import subprocess
# import datetime
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

import pya
# from SiEPIC.ann import qopticParser1 as qp
from enum import Enum
import skrf as rf
from SiEPIC.ann import waveguideNN as wn
from scipy.interpolate import splev, splrep, interp1d

'''
********************************************************************************
This file defines 3 classes:
'Cell' is used to represent a single photonic component by its s-parameters
'Parser' uses a netlist to create a list of 'Cells' and then cascades them 
    into one Cell with the s-matrix of the whole circuit
'Params' extends the pya.Cell class adding the functionality to use the 'Parser'
    class and retrieve the s-parameter data of the circuit as a whole
********************************************************************************
'''


'''
'path' and 'model' are the filepath to the waveguide ANN model and
the model itself, respectively
Both are used as global variables in the 'cascade_netlist' module
'''
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "NN_SiO2_neff.h5")
model = wn.loadWaveguideNN(path)

numInterpPoints = 2000

interpRange = (1.88e+14, 1.99e+14)
#interpRange = (1.93e+14, 1.99e+14)


def strToSci(str):
    '''
    local function to convert strings written in Klayout's 
    exponential notation into floats
    Args:
        str (str): string to convert to float
    Returns:
        float representation of the input string
    '''

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
    '''
    searches for a pin of a specific name in the pin lists of 
    a list of cells. Each pin must be found in two locations.
    On a successful find, the indices of the two cells and the
    indices of the pins in their pin lists are returned
    Args:
        name (str): name of the pin to find
        listofcells (list of 'Cell' type objects): list of the cells to search
    Returns:
        cella (int): index of the first cell where the pin was found
        inda (int): index in the pin list of the first cell where the pin was found
        cellb (int): index of the second cell where the pin was found
        indb (int): index in the pin list of the second cell where the pin was found
    '''

    cella = cellb = inda = indb = -1
    found = False

    #nested for loop search of the pin lists of each cell
    for d in range(0, len(listofcells)):
        for p in range(0, len(listofcells[d].p)):
            if(listofcells[d].p[p] == name):
                cella = d
                inda = p
                found = True
                break
        if found:
            break

    #when the pin is found once, continue searching for the second occurence
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

    #last loop to check if the two occurences of the pin are in the same cell
    if(cellb == -1):
        for p in range(inda+1, len(listofcells[cella].p)):
            if(listofcells[cella].p[p] == name):
                cellb = cella
                indb = p
                break
    
    return [cella, inda, cellb, indb]


class DEVTYPE(Enum):
    '''
    Enum type listing all available component types
    '''

    BDC = 'ebeam_bdc_te1550'
    DC = 'ebeam_dc_halfring_te1550'
    GC = 'ebeam_gc_te1550'
    YB = 'ebeam_y_1550'
    TR = 'ebeam_terminator_te1550'


class Cell():
    '''
    class representing a photonic component as its s-matrix (with related array of 
    frequency values), number of ports, and device ID. Used to simulate the transmission 
    behavior of a photonic circuit. This class is local and should not be confused with 
    the 'pya.Cell' class
    '''

    def __init__(self, id):
        '''
        init function taking an ID
        '''
        self.deviceID = id
        self.devType = None
        self.p = []
        self.iswg = False
        self.wglen = None
        self.wgwid = None
        self.s = None
        self.f = []


    def readSparamFile(self):
        '''
        if the component represented by this Cell object is not a waveguide, its s-parameter information 
        can be extracted from a file from the compact model. This function calls a function that reads and
        parses the appropriate file and then interpolates the data to get a smooth curve of 1000 points for
        each s-matrix element
        Args:
            none
        Returns:
            none
            self.s becomes interpolated s-matrix
            self.f becomes interpolated array of frequency values associated with the s-matrix
        '''

        isgc = False #grating couplers have differently formatted s-param files, requiring a special case
        if(self.devType == DEVTYPE.BDC.value):
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/EBeam_1550_TE_BDC.sparam")
        elif self.devType == DEVTYPE.DC.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/te_ebeam_dc_halfring_straight_gap=30nm_radius=3um_width=520nm_thickness=210nm_CoupleLength=0um.dat")
        elif self.devType == DEVTYPE.GC.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/GC_TE1550_thickness=220 deltaw=0.txt")
            isgc = True
        elif self.devType == DEVTYPE.YB.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/Ybranch_Thickness =220 width=500.sparam")
        elif self.devType == DEVTYPE.TR.value:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/nanotaper_w1=500,w2=60,L=10_TE.sparam")
        else:
            print("ERROR: Unknown Device Type")
            return    
        s, f = pya.Cell.Reader.readSparamData(filename, len(self.p), isgc)
        
        # s and f from the s-param file are interpolated to get a smooth curve
        # and also to match the frequency values for all components
        self.f = np.linspace(interpRange[0], interpRange[1], numInterpPoints)
        func = interp1d(f, s, kind='cubic', axis=0)
        self.s = func(self.f)            


    def wgSparam(self, width_in, thickness_in, deltaLength_in):
        '''
        Function that calculates the s-parameters for a waveguide using the ANN model
        Args:
            None
            self.f (frequency array) and self.wglen (waveguide length) are used to calculate the s-parameters
        Returns:
            None
            self.s becomes the s-matrix calculated by this function
        '''

        mat = np.zeros((len(self.f),2,2), dtype=complex)        
        
        c0 = 299792458 #m/s
        width = width_in #0.5 #um
        thickness = thickness_in #0.22 #um
        mode = 0 #TE
        TE_loss = 700 #dB/m for width 500nm
        alpha = TE_loss/(20*np.log10(np.exp(1))) #assuming lossless waveguide
        waveguideLength = self.wglen + (self.wglen * deltaLength_in)
        
        #calculate wavelength
        wl = np.true_divide(c0,self.f)

        # effective index is calculated by the ANN
        neff = wn.getWaveguideIndex(model,np.transpose(wl),width,thickness,mode)

        #K is calculated from the effective index and wavelength
        K = (2*np.pi*np.true_divide(neff,wl))

        #the s-matrix is built from alpha, K, and the waveguide length
        for x in range(0, len(neff)): 
            mat[x,0,1] = mat[x,1,0] = np.exp(-alpha*waveguideLength + (K[x]*waveguideLength*1j))
        self.s = mat
        

    #calculate waveguide s-parameters based on SiEPIC's compact model
    def wgSparamSiEPIC(self):
        '''
        Calculates waveguide s-parameters based on the SiEPIC compact model for waveguides
        Args:
            None
            self.f (frequency array) and self.wglen (waveguide length) are used to calculate the s-parameters
        Returns:
            None
            self.s becomes the s-matrix calculated by this function        
        '''

        #using file that assumes width 500nm and height 220nm
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sparams/WaveGuideTETMStrip,w=500,h=220.txt")
        with open(filename, 'r') as f:#read info from waveguide s-param file
          coeffs = f.readline().split()
        
        mat = np.zeros((len(self.f),2,2), dtype=complex) #initialize array to hold s-params
        
        c0 = 299792458 #m/s

        #loss calculation
        TE_loss = 700 #dB/m for width 500nm
        alpha = TE_loss/(20*np.log10(np.exp(1)))  

        w = np.asarray(self.f) * 2 * np.pi #get angular frequency from frequency
        lam0 = float(coeffs[0]) #center wavelength
        w0 = (2*np.pi*c0) / lam0 #center frequency (angular)
        
        ne = float(coeffs[1]) #effective index
        ng = float(coeffs[3]) #group index
        nd = float(coeffs[5]) #group dispersion
        
        #calculation of K
        K = 2*np.pi*ne/lam0 + (ng/c0)*(w - w0) - (nd*lam0**2/(4*np.pi*c0))*((w - w0)**2)
        
        for x in range(0, len(self.f)): #build s-matrix from K and waveguide length
          mat[x,0,1] = mat[x,1,0] = np.exp(-alpha*self.wglen + (K[x]*self.wglen*1j))
        
        self.s = mat


    def printPorts(self):
        '''
        print port id's of Cell
        '''
        print("DEVICE ID:", self.deviceID, "has", len(self.p), "port(s).")
        print(self.p)


class Parser:
    '''
    Parser class uses local 'Cell' class and an input netlist to cascade
    the s-matrices of a photonic circuit, simulating its transmission behavior

    'parseFile' parses through the netlist to identify components and gathers their s-parameters
    using 'parseCell'. It collects all these components into its 'cellList'

    'parceCell' takes a netlist entry about a single component and collects or calculates its
    s-parameter data.

    'cascadeCells' takes the cellList gathered by 'parseFile' and cascades all the s-matrices together
    using scikit-rf's 'connect_s' and 'innerconnect_s' functions, deleting already connected Cells as
    it goes. The result is a single Cell object with an s-matrix representing the cascaded circuit
    '''

    def __init__(self, filepath):
        '''
        init function takes a filepath to a netlist that represents a photonic circuit
        '''

        self.cellList = []
        self.nextID = 0
        self.filepath = filepath
        self.nports = 0


    def parseFile(self, width, thickness, deltaLength):
        '''
        reads the netlist file and calls 'parseCell' to create Cell objects from 
        the netlist entries
        Args:
            none
            self.filepath is the needed path to the netlist
        Returns
            none
            the call to 'parseCell' will add a new Cell to self.cellList
        '''

        fid = open(self.filepath)
        lines = fid.readlines()
        for line in lines:
            elements = line.split()
            if len(elements) > 0:
                if (".ends" in elements[0]):
                    break
                elif ("." in elements[0]) or ("*" in elements[0]):
                    continue
                else:
                    self.parseCell(elements, width, thickness, deltaLength)
        

    def parseCell(self, line, width, thickness, deltaLength):
        '''
        This function takes an entry from the netlist and creates a new Cell object
        corresponding to the entry
        
        If the entry is for a waveguide, 'Cell.wgSparam' is called
        to calculate s-parameters based on either the ANN model or the SiEPIC compact
        model
        
        If the entry is for another type of component, 'Cell.readSparamFile' is called
        to read the s-parameter data from a compact model file
        '''

        newCell = Cell(self.nextID)
        self.nextID += 1

        #search the DEVTYPE enum for this entry
        for devtype in DEVTYPE:
            if devtype.value in line[0]:
                newCell.devType = devtype.value
        
        #gather information about the entry into the Cell
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
        
        #call function to collect or calculate s-parameters
        if not newCell.iswg:
            newCell.readSparamFile()
        else:
            newCell.f = np.linspace(interpRange[0], interpRange[1], numInterpPoints)
            # newCell.wgSparam(width, thickness, deltaLength)
            newCell.wgSparamSiEPIC()
        self.cellList.append(newCell)


    def cascadeCells(self):
        '''
        For each pin in the circuit, the s-matrices of the Cells containing that pin are cascaded
        using scikit-rf funtions. 'innerconnect_s' if the two occurances of the pin are in the
        same Cell, 'connect_s' if they are in two different cells

        For a pin:
        * 'findPortMatch' is called to find where the two occurances of the pin are
        * If they are in the same Cell, use 'innerconnect_s' to cascade the s-matrices and delete the
            connected ports from the Cell's port list
        * If they are in different Cells, create a new Cell object and let its s-matrix be the result 
            of 'connect_s' for the two Cells. Delete the two Cells from the cellList

        Repeat this process until all pins have been connected

        One Cell will remain in the cellList. Its s-matrix represents the transmission behavior of the
        circuit as a whole
        '''

        if self.nports == 0:
            return
        for n in range(0, self.nports + 1):
            ca, ia, cb, ib = findPortMatch(str(n), self.cellList)

            #if pin occurances are in the same Cell
            if ca == cb:
                self.cellList[ca].s = rf.innerconnect_s(self.cellList[ca].s, ia, ib)
                del self.cellList[ca].p[ia]
                if ia < ib:
                    del self.cellList[ca].p[ib-1]
                else:
                    del self.cellList[ca].p[ib]

            #if pin occurances are in different Cells
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
        '''
        Return the cellList for a Parser object
        '''
        return self.cellList


    def getCellCount(self):
        '''
        Return the length of the cellList for a Parser object
        '''
        return len(self.cellList)


class Params:
    '''
    class to extend the pya.Cell class, allowing the Cell class
    to parse a netlist and calculate s-parameters for the photonic 
    circuit represented by the current top cell

    also has a method to get the external ports of the circuit
    for use in drawing schematics and plotting simulation 
    results
    '''

    def get_sparameters(filename, width, thickness, deltaLength):
        '''
        function to get the cascaded s-matrix of the photonic circuit 
        represented by the current top-cell in Klayout
        Takes a file name of the netlist representing the circuit
        Args:
            filename (str): name of the netlist
        Returns:
            mat (3D list): s-matrix of the circuit represented by the netlist
            freq (list): array of frequency values corresponding to the entries in 'mat'
        '''

        test = Parser(filename)
        test.parseFile(width, thickness, deltaLength)
        test.cascadeCells()
        mat = test.cellList[0].s
        freq = test.cellList[0].f
        return (mat, freq)
        

    def get_ports(filename, width, thickness, deltaLength):
        '''
        function to get the ports of the cascaded photonic circuit
        Takes a filename of a netlist
        Args: 
            filename (str): name of netlist
        Returns:
            ports (list): ordering of the external ports of the circuit
        '''
        test = Parser(filename)
        test.parseFile(width, thickness, deltaLength)
        test.cascadeCells()
        ports = test.cellList[0].p
        return ports
    
#extending pya.Cell class
pya.Cell.Params = Params
