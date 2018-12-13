
# Enter your Python code here

import tkinter as tk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from SiEPIC.ann import getSparams as gs

import numpy as np

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
        self.parent.title('Circuit Simulation')
        self.parent.geometry('1200x900')
        self.create_menu()
        self.init_figures()
        self.update_magnitude()
        self.generate_phase()
        self.generate_schematic()
        self.parent.after(0, self.parent.deiconify)
        
    def init_figures(self):
        # Schematic figure initialization
        self.schematic = tk.Frame(self.parent, height=850, width=400, relief="ridge", bd=5)
        
        # Magnitude plot initialization
        self.magnitude_plot = tk.Frame(self.parent, width=700, height=400)
        self.mag_fig = Figure(figsize=(7, 4), dpi=100)
        self.mag_ax = self.mag_fig.add_subplot(111)
        self.mag_canvas = FigureCanvasTkAgg(self.mag_fig, master=self.magnitude_plot)
        self.mag_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        self.mag_toolbar = NavigationToolbar2Tk(self.mag_canvas, self.magnitude_plot)
        self.mag_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.BOTH)#, expand=1)
        self.magnitude_plot.grid(column=1)#, fill=tk.BOTH)#, expand=1)
        
        # Phase plot initialization
        self.phase_plot = tk.Frame(self.parent, width=700, height=400)
        self.phase_fig = Figure(figsize=(7, 4), dpi=100)
        self.phase_ax = self.phase_fig.add_subplot(111)
        self.phase_canvas = FigureCanvasTkAgg(self.phase_fig, master=self.phase_plot)
        self.phase_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        self.phase_toolbar = NavigationToolbar2Tk(self.phase_canvas, self.phase_plot)
        self.phase_canvas.get_tk_widget().pack(side=tk.TOP)
        self.phase_plot.grid(column=1)
        
    def update_magnitude(self):
        ##frame = self.magnitude_plot
        ##fig = Figure(figsize=(7, 4), dpi=100)
        s, f = gs.getSparams()
        tera = 1e12
        f = np.divide(f, tera)
        ##ax = self.mag_fig.add_subplot(111)]
        self.mag_ax.clear()
        self.mag_ax.plot(f, abs(s[:,0,2])**2)
        self.mag_ax.set_xlabel('Frequency (THz)')
        self.mag_ax.set_ylabel(r'$|A| ^2$')
        self.mag_ax.set_title('Magnitude-Squared')
        ##canvas = FigureCanvasTkAgg(fig, master=frame)
        self.mag_canvas.draw()
        ##canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        ##toolbar = NavigationToolbar2Tk(canvas, frame)
        self.mag_toolbar.update()
        ##canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.BOTH)#, expand=1)
        ##frame.grid(column=1)
    
    def generate_phase(self):
        ##frame = self.phase_plot
        ##fig = Figure(figsize=(7, 4), dpi=100)
        s, f = gs.getSparams()
        tera = 1e12
        f = np.divide(f, tera)
        ##ax = fig.add_subplot(111)
        self.phase_ax.clear()
        self.phase_ax.plot(f, np.rad2deg(np.unwrap(np.angle(s[:,0,2]))))
        self.phase_ax.set_xlabel('Frequency (THz)')
        self.phase_ax.set_title('Phase')
        ##canvas = FigureCanvasTkAgg(fig, master=frame)
        self.phase_canvas.draw()
        ##canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        ##toolbar = NavigationToolbar2Tk(canvas, frame)
        self.phase_toolbar.update()
        ##canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.BOTH)#, expand=1)
        ##frame.grid(column=1)
        
    def generate_schematic(self):
        frame = self.schematic
        frame.grid(row=0, column=0, rowspan=2)
    
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
        filemenu.add_command(label="Exit", command=self._quit)
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