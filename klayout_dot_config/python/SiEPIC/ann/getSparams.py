
# Enter your Python code here

import pya
import os
from SiEPIC.ann import export_netlist as en # import this!
from SiEPIC.ann import cascade_netlist as cn # import this!

fname = 'singleComp0'
netname = '_netlist' + fname + '.txt'
matname = fname + '.mat'
freqname = 'freq' + fname + '.mat'
orig_cwd = os.getcwd()
temp_cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")

def getSparams():
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    # Get the current topcell from Klayout
    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    # Get the netlist from the cell
    text_subckt, text_main, = cell.spice_netlist_export(verbose=True)
    #print(dir(cell))
    # Write the netlist to a temporary file
    fid = open(netname, 'w')
    fid.write(text_subckt)
    fid.close()
    # Get sparams and freq array from netlist
    s, f = cell.Params.get_sparameters(netname) 
    # Change the working directory back to what it was originally, 
    # out of politeness and an abundance of caution
    os.chdir(orig_cwd)
    # Return the sparameters and the frequency array
    return s, f
    
def getPorts():
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    # Get the current topcell from Klayout
    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    # Get port list
    p = cell.Params.get_ports(netname) 
    # Change the working directory back to what it was originally, 
    # out of politeness and an abundance of caution
    os.chdir(orig_cwd)
    # Return the sparameters and the frequency array
    return p
    
def plot_magnitude():
    import matplotlib.pyplot as plt
    s, f = getSparams()
    plt.plot(f, abs(s[:,0,2])**2)
    plt.xlabel('Frequency (THz)')
    plt.title('Magnitude^2')
    plt.show()
    #print(len(s[:,0,2]))
    #print(len(f))
    
def plot_phase():
    import matplotlib.pyplot as plt
    import numpy as np
    s, f = getSparams()
    #plt.plot(f, np.rad2deg(np.unwrap(np.angle(s[:,0,2]))))
    plt.plot(f, np.unwrap(np.angle(s[:,0,2])))
    plt.xlabel('Frequency (THz)')
    plt.title('Phase (deg)')
    plt.show()

def create_matlab_files():
    import scipy.io as sio
    # First, change the current working directory because we'll be saving files
    os.chdir(temp_cwd)
    sio.savemat(matname, mdict={'sparams':s})
    sio.savemat(freqname, mdict={'freq':f})
    # Change the working directory back to what it was originally, 
    # out of politeness and an abundance of caution
    os.chdir(orig_cwd)