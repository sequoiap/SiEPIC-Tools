import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.backend_bases import key_press_handler
# from matplotlib.figure import Figure

from SiEPIC.ann import getSparams as gs
from SiEPIC.ann import NetlistDiagram
from SiEPIC.ann.layout.graphing.graph import Graph, DataSet, MenuItem
import SiEPIC._globals as glob

from SiEPIC.ann.simulation import Simulation

import scipy.io as sio
import numpy as np
import os

class TkRoot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.withdraw()
        self.after(0, self.deiconify)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        self.withdraw()
        self.quit()
        self.destroy()

class CircuitAnalysisGUI():

    # Some constants
    tera = 1e12
    nano = 1e9

    def __init__(self, parent):
        self.parent = parent

        # Hide the parent until the whole window has loaded.
        self.parent.withdraw()

        # Set the window title and size
        self.parent.title('Circuit Simulation')
        w = 900 # width for the Tk root
        h = 900 # height for the Tk root
        ws = self.parent.winfo_screenwidth() # width of the screen
        hs = self.parent.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws - w) / 2
        y = (hs - h) / 2
        # set the dimensions of the screen and where it is placed
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

        # Initialize the menu and figures
        self.create_menu()
        self.init_figures()

        self.simulation = Simulation()

        self.plotFrequency = True

        # Update magnitude and phase generates the netlist, and therefore
        # need to be placed before generate_schematic
        self.set_controls()
        self.generate_schematic()

        # Now that everything is in place, show the window.
        self.parent.after(0, self.parent.deiconify)

    def create_menu(self):
        # Create the toplevel menubar
        menubar = tk.Menu(self.parent)
        
        # Add the pulldown menus with their options, then add it to the menubar
        filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Open")
        # filemenu.add_command(label="Save")
        # filemenu.add_command(label="Enlarge Schematic", command=self.open_schematic)
        filemenu.add_command(label="Export s-matrix to .mat", command=self.export_s_matrix_mat)
        filemenu.add_command(label="Exit", command=self.parent.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # Configure the menubar
        self.parent.config(menu=menubar)

    def init_figures(self):
        # Port selection menu
        self.controls = tk.Frame(self.parent, width=700, height=30, bd=1)
        self.controls.grid(row=0, column=0)
        # Schematic figure initialization
        self.schematic_height = 900
        self.schematic_width = 900
        self.schematic = tk.Frame(self.parent, height=self.schematic_height, width=self.schematic_width)
        self.schematic.grid(row=1, column=0)

    def set_controls(self):
        options = self.simulation.external_port_list
        self.first = tk.StringVar(self.parent)
        self.first.set(options[0])
        self.second = tk.StringVar(self.parent)
        self.second.set(options[0])

        tk.Label(self.controls, text="From: ").grid(row=0, column=0)
        thing2 = tk.OptionMenu(self.controls, self.first, *options)
        thing2.grid(row=0, column=1)

        tk.Label(self.controls, text=" to: ").grid(row=0, column=2)

        thing4 = tk.OptionMenu(self.controls, self.second, *options)
        thing4.grid(row=0, column=3)

        gobtn = tk.Button(self.controls, text="Plot", command=self.selection_changed).grid(row=0, column=4)
        tk.Label(self.controls, text=" Charts: ").grid(row=0, column=5)
        tk.Button(self.controls, text="Magnitude", command=self.open_magnitude).grid(row=0, column=6)
        tk.Button(self.controls, text="Phase", command=self.open_phase).grid(row=0, column=7)
        tk.Button(self.controls, text="Layout", command=self.open_layout).grid(row=0, column=8)

        self.magnitude = None
        self.phase = None

    def generate_schematic(self):
        NetlistDiagram.run()
        wd = os.getcwd()
        temppath = glob.TEMP_FOLDER
        os.chdir(temppath)
        original = Image.open("Schematic.png")
        resized = original.resize((870, 895), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(resized)
        label = tk.Label(self.schematic, image=img)
        label.image = img
        label.bind("<Button-1>", self.open_schematic)
        label.pack()
        os.chdir(wd)

    def export_s_matrix_mat(self):
        fileTypes = [("MATLAB file","*.mat")]
        options = {}
        options['initialdir'] = os.path.expanduser('~')
        options['filetypes'] = fileTypes
        options['parent'] = self.parent
        filename = filedialog.asksaveasfilename(**options)
        if filename:
            s_mat, freq = self.simulation.exportSMatrix()
            sio.savemat(filename, {'s_mat' : s_mat, 'freq' : freq})

        
    def plotByFrequency(self):
        if not self.plotFrequency:
            self.plotFrequency = True
            lines = self.magnitude.get_lines()
            for line in lines.values():
                x = line.x
                line.x = self.wavelengthToFrequency(x / CircuitAnalysisGUI.nano) / CircuitAnalysisGUI.tera
                line.objectID.set_xdata(line.x)
            self.magnitude.refresh()
            self.magnitude.xlabel('Frequency (THz)')
            lines = self.phase.get_lines()
            for line in lines.values():
                x = line.x
                line.x = self.wavelengthToFrequency(x / CircuitAnalysisGUI.nano) / CircuitAnalysisGUI.tera
                line.objectID.set_xdata(line.x)
            self.phase.refresh()
            self.phase.xlabel('Frequency (THz)')


    def plotByWavelength(self):
        if self.plotFrequency:
            self.plotFrequency = False
            lines = self.magnitude.get_lines()
            for line in lines.values():
                x = line.x
                line.x = self.frequencyToWavelength(x * CircuitAnalysisGUI.tera) * CircuitAnalysisGUI.nano
                line.objectID.set_xdata(line.x)
            self.magnitude.refresh()
            self.magnitude.xlabel('Wavelength (nm)')
            lines = self.phase.get_lines()
            for line in lines.values():
                x = line.x
                line.x = self.frequencyToWavelength(x * CircuitAnalysisGUI.tera) * CircuitAnalysisGUI.nano
                line.objectID.set_xdata(line.x)
            self.phase.refresh()
            self.phase.xlabel('Wavelength (nm)')

    def additional_menus(self):
        functions = [MenuItem("Plot by frequency", self.plotByFrequency), MenuItem("Plot by wavelength", self.plotByWavelength)]
        addon_menu = {"Data": functions}
        return addon_menu

    def open_magnitude(self):
        if self.magnitude is None:
            self.magnitude = Graph(self.parent, "Magnitude", additional_menus=self.additional_menus(), onCloseCallback=self._magnitude_closed)
            self.magnitude.ylabel(r'$|A| ^2$')
            self.magnitude.title('Magnitude-Squared')
        else:
            self.magnitude.raise_window()

    def _magnitude_closed(self):
        self.magnitude = None

    def open_phase(self):
        if self.phase is None:
            self.phase = Graph(self.parent, "Phase", additional_menus=self.additional_menus(), onCloseCallback=self._phase_closed)
            self.phase.ylabel('Phase (rad)')
            self.phase.title('Phase')
        else:
            self.phase.raise_window()

    def _phase_closed(self):
        self.phase = None

    def open_layout(self):
        import SiEPIC.ann.layout.schematic as schem
        comp = self.simulation.external_components
        fig = schem.SchematicDrawer(self.parent, comp)
        fig.draw()

    def frequencyToWavelength(self, frequencies):
        c = 299792458
        return c / frequencies

    def wavelengthToFrequency(self, wavelengths):
        c = 299792458
        return c / wavelengths

    def update_magnitude(self, fromPort=0, toPort=0, name=None):
        if self.plotFrequency == True:
            self.magnitude.plot(*self.simulation.getMagnitudeByFrequencyTHz(fromPort, toPort), name=name)
            self.magnitude.xlabel('Frequency (THz)')
        else:
            self.magnitude.plot(*self.simulation.getMagnitudeByWavelengthNm(fromPort, toPort), name=name)
            self.magnitude.xlabel('Wavelength (nm)')
    
    def update_phase(self, fromPort=0, toPort=0, name=None):
        if self.plotFrequency == True:
            self.phase.plot(*self.simulation.getPhaseByFrequencyTHz(fromPort, toPort), name)
            self.phase.xlabel('Frequency (THz)')
        else:
            self.phase.plot(*self.simulation.getPhaseByWavelengthNm(fromPort, toPort), name)
            self.phase.xlabel('Wavelength (nm)')

    def open_schematic(self, event):
        import subprocess, os, sys
        wd = os.getcwd()
        temppath = glob.TEMP_FOLDER
        os.chdir(temppath)
        filepath = "Schematic.png"
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt': # For Windows
            os.startfile(filepath)
        elif os.name == 'posix': # For Linux, Mac, etc.
            subprocess.call(('xdg-open', filepath))
        os.chdir(wd)
        
    def selection_changed(self):#, event):
        fromPort = self.first.get()
        toPort = self.second.get()
        try:
            self.update_magnitude(int(self.first.get()) - 1, int(self.second.get()) - 1, str(fromPort) + "_to_" + str(toPort))
        except:
            pass
        try:
            self.update_phase(int(self.first.get()) - 1, int(self.second.get()) - 1, str(fromPort) + "_to_" + str(toPort))
        except:
            pass
    
    def _quit(self):
        self.parent.withdraw()
        self.parent.quit()
        self.parent.destroy()
        
def circuit_analysis():
    root = TkRoot()
    app = CircuitAnalysisGUI(root)
    root.mainloop()

class TimeANN:
    def __init__(self):
        self.root = TkRoot()

    def time_circuit_analysis(self):
        self.app = CircuitAnalysisGUI(self.root)
    
if __name__ == "__main__":
    import timeit    
    setup="""\
import os
print(os.getcwd())
from SiEPIC.ann.circuit_simulation import TimeANN
obj = TimeANN()
"""
    time = timeit.timeit('obj.time_circuit_analysis()', setup=setup, number=1)
    print(time)
