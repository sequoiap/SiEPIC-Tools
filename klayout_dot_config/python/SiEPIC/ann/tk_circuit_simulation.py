
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
        self.generate_schematic()
        self.update_magnitude()
        self.update_phase()
        # Now that everything is in place, show the window.
        self.parent.after(0, self.parent.deiconify)
        
    def init_figures(self):
        # Schematic figure initialization
        self.schematic = tk.Frame(self.parent, height=870, width=895, relief="ridge", bd=5)
        self.schematic.grid(row=0, column=0, rowspan=2)
        
        # Magnitude plot initialization
        self.magnitude_plot = tk.Frame(self.parent, width=700, height=400)
        self.mag_fig = Figure(figsize=(7, 4), dpi=100)
        self.mag_ax = self.mag_fig.add_subplot(111)
        self.mag_canvas = FigureCanvasTkAgg(self.mag_fig, master=self.magnitude_plot)
        self.mag_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        self.mag_toolbar = NavigationToolbar2Tk(self.mag_canvas, self.magnitude_plot)
        self.mag_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.BOTH)#, expand=1)
        self.magnitude_plot.grid(row=0, column=1)#, fill=tk.BOTH)#, expand=1)
        
        # Phase plot initialization
        self.phase_plot = tk.Frame(self.parent, width=700, height=400)
        self.phase_fig = Figure(figsize=(7, 4), dpi=100)
        self.phase_ax = self.phase_fig.add_subplot(111)
        self.phase_canvas = FigureCanvasTkAgg(self.phase_fig, master=self.phase_plot)
        self.phase_canvas.get_tk_widget().pack(side=tk.TOP)#, fill=tk.X)#, expand=1)
        self.phase_toolbar = NavigationToolbar2Tk(self.phase_canvas, self.phase_plot)
        self.phase_canvas.get_tk_widget().pack(side=tk.TOP)
        self.phase_plot.grid(row=1, column=1)
        
    def update_magnitude(self):
        # Get s parameters and frequencies
        s, f = gs.getSparams()
        # Convert from Hz to THz
        tera = 1e12
        f = np.divide(f, tera)
        # Clear whatever is on the plot, overlay new graph
        self.mag_ax.clear()
        self.mag_ax.plot(f, abs(s[:,0,2])**2)
        # Label the plot
        self.mag_ax.set_xlabel('Frequency (THz)')
        self.mag_ax.set_ylabel(r'$|A| ^2$')
        self.mag_ax.set_title('Magnitude-Squared')
        # Draw on the canvas, update the toolbar
        self.mag_canvas.draw()
        self.mag_toolbar.update()
    
    def update_phase(self):
        # Get s parameters and frequencies
        s, f = gs.getSparams()
        # Convert from Hz to THz
        tera = 1e12
        f = np.divide(f, tera)
        # Clear whatever is on the plot, overlay new graph
        self.phase_ax.clear()
        # Label the plot
        self.phase_ax.plot(f, np.rad2deg(np.unwrap(np.angle(s[:,0,2]))))
        self.phase_ax.set_xlabel('Frequency (THz)')
        self.phase_ax.set_title('Phase')
        # Draw on the canvas, update the toolbar
        self.phase_canvas.draw()
        self.phase_toolbar.update()
        
    def generate_schematic(self):
        return
    
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