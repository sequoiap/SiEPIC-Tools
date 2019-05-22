
# Enter your Python code here

import pya
import os
from SiEPIC.ann import netlist as cn
import SiEPIC._globals as glob

fname = 'singleComp0'
netname = '_netlist' + fname + '.txt'
matname = fname + '.mat'
freqname = 'freq' + fname + '.mat'
orig_cwd = os.getcwd()
temp_cwd = glob.TEMP_FOLDER

def generateNetlist():
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    # Get the current topcell from Klayout
    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    # Get the netlist from the cell
    text_subckt, text_main = cell.spice_netlist_export_ann(verbose=False)
    #print(dir(cell))
    # Write the netlist to a temporary file
    fid = open(netname, 'w')
    fid.write(text_subckt)
    fid.close()


def getSparams(width, thickness, lengthDelta):
    generateNetlist()

    # Get sparams and freq array from netlist
    s, f = cn.Params.get_sparameters(netname, width, thickness, lengthDelta) 
    # Change the working directory back to what it was originally, 
    # out of politeness and an abundance of caution
    os.chdir(orig_cwd)
    # Return the sparameters and the frequency array
    return s, f
    
def getPorts(width, thickness, lengthDelta):
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    # Get the current topcell from Klayout
    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    # Get port list
    p = cell.Params.get_ports(netname, width, thickness, lengthDelta) 
    # Change the working directory back to what it was originally, 
    # out of politeness and an abundance of caution
    os.chdir(orig_cwd)
    # Return the sparameters and the frequency array
    return p
