
# Enter your Python code here

import pya
import os
from SiEPIC.ann import netlist as cn
import SiEPIC._globals as glob
import json

netname = 'netlist.txt'
orig_cwd = os.getcwd()
temp_cwd = glob.TEMP_FOLDER

externals = None
siepic_netlist_text = None
ann_netlist_text = None
ann_netlist_model = None

def generateNetlist():
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    # Get the current topcell from Klayout
    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    # Get the netlist from the cell
    global siepic_netlist_text, ann_netlist_text, ann_netlist_model
    siepic_netlist_text, ann_netlist_text, ann_netlist_model = cell.spice_netlist_export_ann()
    #print(dir(cell))
    # Write the netlist to a temporary file
    with open(netname, 'w') as fid:
        fid.write(siepic_netlist_text)


def getSparams():
    generateNetlist()

    # Get sparams and freq array from netlist
    s, f, ends = cn.get_sparameters(ann_netlist_model) 
    global externals
    externals = ends
    # Change the working directory back to what it was originally, 
    # out of politeness and an abundance of caution
    os.chdir(orig_cwd)
    # Return the sparameters and the frequency array
    return s, f
    
def getPorts():
    global externals
    if externals:
        return externals