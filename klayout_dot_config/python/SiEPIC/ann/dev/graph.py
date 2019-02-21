import tkinter as tk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

class Graph:
    def __init__(self, master):
        self.master = master
        master.title("Graph")
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)  # A tk.DrawingArea.
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.mpl_connect("key_press_event", self.on_key_press)

    def plot(self, x, y):
        self.ax.plot(x, y)
        self.canvas.draw()

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)

    def title(self, title):
        self.master.title(title)
        self.ax.set_title(title)
        self.canvas.draw()

    def xlabel(self, xlabel):
        self.ax.set_xlabel(xlabel)
        self.canvas.draw()

    def ylabel(self, ylabel):
        self.ax.set_ylabel(ylabel)
        self.canvas.draw()

    def close_windows(self):
        self.master.destroy()

def test(): 
    root = tk.Tk()

    app = Graph(tk.Toplevel(root))
    t = np.arange(0, 3, .01)
    app.plot(t, 2 * np.sin(2 * np.pi * t))
    app.title("Frequency Response")
    app.xlabel("Time (s)")
    app.ylabel("Amplitude")

    app2 = Graph(tk.Toplevel(root))
    app2.plot(t, 5 * np.cos(2 * np.pi * t))

    root.mainloop()

if __name__=="__main__":
    test()