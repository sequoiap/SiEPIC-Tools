
import tkinter as tk
from PIL import Image, ImageTk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from SiEPIC.ann import getSparams as gs
from SiEPIC.ann import NetlistDiagram

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

class CircuitSimulationGUI():
    def __init__(self, parent):
        self.parent = parent
        # Hide the parent until the whole window has loaded.
        self.parent.withdraw()
        # Set the window title and size
        self.parent.title('Circuit Simulation')
        w = 1600 # width for the Tk root
        h = 900 # height for the Tk root
        # get screen width and height
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
        # parameters for generating waveguide s parameters
        waveguideWidth = 0.5
        waveguideThickness = 0.22
        # Get s parameters and frequencies (generates the netlist, too).
        self.s, self.f = gs.getSparams(waveguideWidth, waveguideThickness)
        # Update magnitude and phase generates the netlist, and therefore
        # need to be placed before generate_schematic
        self.update_magnitude()
        self.update_phase()
        self.set_controls()
        self.generate_schematic()
        self.ports = gs.getPorts()
        # Now that everything is in place, show the window.
        self.parent.after(0, self.parent.deiconify)
        
    def init_figures(self):
        # Schematic figure initialization
        self.schematic_height = 920
        self.schematic_width = 895
        self.schematic = tk.Frame(self.parent, height=self.schematic_height, width=self.schematic_width)#, relief="ridge", bd=5)
        self.schematic.grid(row=0, column=0, rowspan=3)
        
        # Port selection menu
        self.controls = tk.Frame(self.parent, width=700, height=30, bd=1)
        self.controls.grid(row=0, column=1)
        
        # Magnitude plot initialization
        self.magnitude_plot = tk.Frame(self.parent, width=700, height=400)
        self.mag_fig = Figure(figsize=(7, 4), dpi=100)
        self.mag_ax = self.mag_fig.add_subplot(111)
        self.mag_canvas = FigureCanvasTkAgg(self.mag_fig, master=self.magnitude_plot)
        self.mag_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        self.mag_toolbar = NavigationToolbar2Tk(self.mag_canvas, self.magnitude_plot)
        self.mag_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.BOTH)#, expand=1)
        self.magnitude_plot.grid(row=1, column=1)#, fill=tk.BOTH)#, expand=1)
        
        # Phase plot initialization
        self.phase_plot = tk.Frame(self.parent, width=700, height=400)
        self.phase_fig = Figure(figsize=(7, 4), dpi=100)
        self.phase_ax = self.phase_fig.add_subplot(111)
        self.phase_canvas = FigureCanvasTkAgg(self.phase_fig, master=self.phase_plot)
        self.phase_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        self.phase_toolbar = NavigationToolbar2Tk(self.phase_canvas, self.phase_plot)
        self.phase_canvas.get_tk_widget().pack(side=tk.TOP)
        self.phase_plot.grid(row=2, column=1)
        
    def set_controls(self):
        options = NetlistDiagram.getExternalPortList()
        thing1 = tk.Label(self.controls, text="From: ").grid(row=0, column=0)#.pack(side=tk.LEFT)
        self.first = tk.StringVar(self.parent)
        self.first.set(options[0])
        self.second = tk.StringVar(self.parent)
        self.second.set(options[0])
        thing2 = tk.OptionMenu(self.controls, self.first, *options, command=self.selection_changed)
        thing2.config(width=20)
        thing2.grid(row=0, column=1)#.pack(side=tk.LEFT)
        thing3 = tk.Label(self.controls, text=" to: ").grid(row=0, column=2)#.pack(side=tk.LEFT)
        thing4 = tk.OptionMenu(self.controls, self.second, *options, command=self.selection_changed)
        thing4.config(width=20)
        thing4.grid(row=0, column=3)#.pack(side=tk.LEFT)
        #gobtn = tk.Button(self.controls, text="GO").grid(row=0, column=4)#.pack(side=tk.LEFT) #command=func)
                        
    def update_magnitude(self, fromPort=0, toPort=0):
        # Get s parameters and frequencies
        #s, f = gs.getSparams()
        s, f = self.s, self.f
        # Convert from Hz to THz
        tera = 1e12
        f = np.divide(f, tera)
        # Clear whatever is on the plot, overlay new graph
        self.mag_ax.clear()
        self.mag_ax.plot(f, abs(s[:,fromPort,toPort])**2)
        # Label the plot
        self.mag_ax.set_xlabel('Frequency (THz)')
        self.mag_ax.set_ylabel(r'$|A| ^2$')
        self.mag_ax.set_title('Magnitude-Squared')
        # Draw on the canvas, update the toolbar
        self.mag_canvas.draw()
        self.mag_toolbar.update()
    
    def update_phase(self, fromPort=0, toPort=0):
        # Get s parameters and frequencies
        #s, f = gs.getSparams()
        s, f = self.s, self.f
        # Convert from Hz to THz
        tera = 1e12
        f = np.divide(f, tera)
        # Clear whatever is on the plot, overlay new graph
        self.phase_ax.clear()
        # Label the plot
        self.phase_ax.plot(f, np.rad2deg(np.unwrap(np.angle(s[:,fromPort,toPort]))))
        self.phase_ax.set_xlabel('Frequency (THz)')
        self.phase_ax.set_title('Phase')
        # Draw on the canvas, update the toolbar
        self.phase_canvas.draw()
        self.phase_toolbar.update()
        
    def open_schematic(self, event):
        import subprocess, os, sys
        wd = os.getcwd()
        temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
        os.chdir(temppath)
        filepath = "Schematic.png"
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt': # For Windows
            os.startfile(filepath)
        elif os.name == 'posix': # For Linux, Mac, etc.
            subprocess.call(('xdg-open', filepath))
        os.chdir(wd)
        
    def port2idx(self, port):
        port = -port;
        print(self.ports)
        port = str(port)
        if port in self.ports:
            return self.ports.index(port)
        else:
            raise Exception("port2idx function malfunctioned.")
        
    def selection_changed(self, event):
        self.update_magnitude(self.port2idx(int(self.first.get())), self.port2idx(int(self.second.get())))
        self.update_phase(self.port2idx(int(self.first.get())), self.port2idx(int(self.second.get())))
        
    def generate_schematic(self):
        NetlistDiagram.run()
        wd = os.getcwd()
        temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
        os.chdir(temppath)
        original = Image.open("Schematic.png")
        resized = original.resize((870, 895), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(resized)
        label = tk.Label(self.schematic, image=img)
        label.image = img
        label.bind("<Button-1>", self.open_schematic)
        label.pack()
        os.chdir(wd)
    
    def _quit(self):
        self.parent.withdraw()
        self.parent.quit()
        self.parent.destroy()
        
    def create_menu(self):
        # Create the toplevel menubar
        menubar = tk.Menu(self.parent)
        
        # Add the pulldown menus with their options, 
        # then add it to the menubar
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save")
        #filemenu.add_command(label="Enlarge Schematic", command=self.open_schematic)
        filemenu.add_command(label="Exit", command=self.parent.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # Configure the menubar
        self.parent.config(menu=menubar)
        
def circuit_analysis():
    #root = tk.Tk()
    root = TkRoot()
    app = CircuitSimulationGUI(root)
    root.mainloop()
        
if __name__=="__main__":
    root = TkRoot()
    app = CircuitSimulationGUI(root)
    root.mainloop()