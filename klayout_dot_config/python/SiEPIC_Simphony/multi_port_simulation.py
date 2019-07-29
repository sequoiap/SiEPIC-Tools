# """
# multi_port_simulation.py

# Author:
#     Sequoia Ploeg

# Dependencies:
# - tkinter
# - simphony
# - scipy
# - numpy
# - os
# - matplotlib

# This file mainly provides the GUI for running simulations. It creates a 
# Simulation object, runs it, and provides controls and windows for displaying
# and exporting the results.
# """

# import pya
# import tkinter as tk
# from tkinter import filedialog

# from .graph import Graph, DataSet, MenuItem
# from simphony.simulation import MultiInputSimulation

# import scipy.io as sio
# import numpy as np
# import os

# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.backend_bases import key_press_handler
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt

# class CircuitAnalysisGUI(tk.Tk):
#     # Some constants
#     tera = 1e12
#     nano = 1e9

#     def __init__(self):
#         tk.Tk.__init__(self)
#         self.withdraw()
#         self.after(0, self.deiconify)
#         self.protocol("WM_DELETE_WINDOW", self.on_closing)

#         # Title the window
#         self.title('Multi-Input Circuit Simulation')

#         # Run the simulation
#         cell = pya.Application.instance().main_window().current_view().active_cellview().cell
#         _, _, ann_netlist_model = cell.spice_netlist_export_ann()
#         self.simulation = MultiInputSimulation(ann_netlist_model)

#         # Object paddings
#         self.padx = 5
#         self.pady = 5

#         # One frame to rule them all
#         bbox = tk.Frame(padx=self.padx, pady=self.pady)
#         bbox.pack()

#         # Controls frame
#         self.controls = tk.Frame(bbox, bd=1)
#         self.controls.grid(row=0, column=0, sticky='EW')
#         self.generate_controls()

#         # Schematic figure initialization
#         self.schematic = tk.Frame(bbox)
#         self.schematic.grid(row=1, column=0)
#         self.generate_schematic()

#         # Now that everything is in place, show the window.
#         self.after(0, self.deiconify)

#     def on_closing(self):
#         self.withdraw()
#         self.quit()
#         self.destroy()

#     def generate_controls(self):
#         io_group = tk.LabelFrame(self.controls, text="Input/Output", padx=self.padx, pady=self.pady)
#         io_group.pack(fill=tk.BOTH, expand=1)
#         tk.Label(io_group, text="Input ports (period separated):").grid(row=0, column=0, sticky='EW')
#         self.in_port = tk.Entry(io_group)
#         self.in_port.grid(row=1, column=0, sticky='EW')
#         tk.Label(io_group, text="Output ports (period separated):").grid(row=0, column=1, sticky='EW')
#         self.out_port = tk.Entry(io_group)
#         self.out_port.grid(row=1, column=1, sticky='EW')
#         tk.Button(io_group, text="Run Simulation", command=self.plot).grid(row=2, column=1, sticky='E')
#         self.bind('<Return>', self.plot)
#         self.bind('<KP_Enter>', self.plot)

#     def generate_schematic(self):
#         """
#         This function creates a figure object and places it within the 
#         schematic slot in the parent tkinter window. It then calls 'draw' to 
#         plot the layout points on the canvas.
#         """
#         # The only real objects we'll need to interact with to plot and unplot
#         self.components = self.simulation.external_components
#         self.fig = Figure(figsize=(5, 4), dpi=100)

#         # Objects needed simply for the sake of embedding the graph in tk
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.schematic)
#         self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#         self.fig.clear()
#         self.ax = self.fig.add_subplot(111)
#         self.draw()

#     def draw(self):
#         for comp in self.components:
#             self.ax.plot(comp.lay_x, comp.lay_y, 'ro')
#             externals = [int(x) for x in comp.nets if int(x) < 0 ]
#             self.ax.text(comp.lay_x, comp.lay_y, "  Port " + str(-externals[0]) + ": " + comp.__class__.__name__)
#         self.ax.axis('off')
#         self.canvas.draw()

#     def plot(self, *args, **kwargs):
#         in_ports = [int(i) - 1 for i in self.in_port.get().split('.')]
#         out_ports = [int(i) - 1 for i in self.out_port.get().split('.')]
#         self.simulation.multi_input_simulation(inputs=in_ports)
#         plt.figure()
#         for output in out_ports:
#             plt.plot(*self.simulation.get_magnitude_by_frequency_thz(output), label=("out_" + str(output + 1)))
#         plt.title('Multiple Input Simulation')
#         plt.xlabel('Frequency (THz)')
#         plt.ylabel('Gain')
#         plt.legend()
#         plt.draw()
#         plt.show()
        
# def circuit_analysis():
#     try:
#         cell = pya.Application.instance().main_window().current_view().active_cellview().cell
#         app = CircuitAnalysisGUI()
#         app.mainloop()
#     except Exception:
#         raise

# if __name__ == "__main__":
#     circuit_analysis()