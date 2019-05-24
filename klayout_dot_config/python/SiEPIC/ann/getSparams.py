
# Enter your Python code here

import pya
import os
from SiEPIC.ann import netlist as cn
import SiEPIC._globals as glob
import json

netname = 'netlist.txt'
orig_cwd = os.getcwd()
temp_cwd = glob.TEMP_FOLDER

def generateNetlist():
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    # Get the current topcell from Klayout
    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    # Get the netlist from the cell
    text_subckt, output = cell.spice_netlist_export_ann()
    #print(dir(cell))
    # Write the netlist to a temporary file
    with open(netname, 'w') as fid:
        fid.write(text_subckt)
    with open('netlist.json', 'w') as outfile:
        json.dump(output, outfile, indent=2)


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
