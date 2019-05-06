import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import scipy.io as sio
import os # For filedialog to start in user's /~ instead of /.

class SchematicDrawer:
    def __init__(self, parent : tk.Toplevel, components):
        self.components = components
        # The master tk object
        self.parent = parent
        self.master = tk.Toplevel(parent)
        # self.master = parent
        self.master.title("Layout")

        # The only real objects we'll need to interact with to plot and unplot
        self.fig = Figure(figsize=(5, 4), dpi=100)

        # Objects needed simply for the sake of embedding the graph in tk
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

    def draw(self):
        for comp in self.components:
            self.ax.plot(comp.posx, comp.posy, 'ro')
            externals = [x for x in comp.ports if x < 0 ]
            self.ax.text(comp.posx, comp.posy, "  Port " + str(-externals[0]) + ": " + comp.label)
        self.ax.axis('off')
        self.canvas.draw()