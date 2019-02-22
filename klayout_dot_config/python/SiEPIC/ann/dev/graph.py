"""
Tkinter Graph Wrapper

This module allows tkinter graphs to be easily created from a parent tkinter object
in their own separate windows.

Dependencies:
    - tkinter
    - matplotlib
    - numpy
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

class DataSet:
    """
    The DataSet class is used to allow the Graph to conveniently store and access multiple lines.

    This class is not intended to be used by any other class besides Graph.
    Stored within the DataSet class is the xdata, the ydata, and an optional name.
    Graph generates a DataSet object when xdata, ydata, and an optional name is passed to its
    plot function. Upon graphing the object, it stores a reference to the axis line object.
    Graph stores a list of DataSet objects. In this way, it can iterate through all the axis
    line objects to delete or otherwise modify them.
    """

    def __init__(self, x: np.array, y: np.array, name: str = None):
        """Stores the x and y values of the plot, as well as an (optional) name for the DataSet"""

        self.x = x
        self.y = y
        self.name = name

    def setObjectID(self, id):
        """The objectID member is intended to hold a reference to a matplotlib Axes line."""

        self.objectID = id[0]

    def getObjectID(self):
        """The objectID member holds a reference to a matplotlib Axes line."""

        return self.objectID

    def __str__(self):
        return self.name

class Graph:
    """
    The Graph class presents a tkinter interface for Matplotlib plots.

    It requires a Toplevel tkinter object for initialization. 
    
    Attributes
    ----------
    default_title : str
        The default title for a new or reset window and plot.
    master : tk.Toplevel
    fig : matplotlib.figure.Figure
    canvas : matplotlib.backends.backend_tkagg.FigureCanvasTkAgg
    toolbar: matplotlib.backends.backend_tkagg.NavigationToolbar2Tk
    ax : matplotlib.axes.Axes
    hasLegend : boolean
    lines : DataSet[]

    Methods
    -------
    reset()
        Clears the figure, adds a new axis, resets the title, and clears all stored DataSet lines.
    plot(x=None, y=None, name=None)
        Plots x and y data on a Graph.
    clear()
    legend()
    linewidth()
    on_key_press()
    title(title)
        Sets the window title and the graph title.
    xlabel(xlabel)
        Sets the x-axis label.
    ylabel(ylabel)
        Sets the y-axis label.
    close_windows()
    """

    # Default window and plot title
    default_title = "Graph"

    def __init__(self, master: tk.Toplevel):
        # The master tk object
        self.master = master

        # The only real objects we'll need to interact with to plot and unplot
        self.fig = Figure(figsize=(5, 4), dpi=100)

        # Objects needed simply for the sake of embedding the graph in tk
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.mpl_connect("key_press_event", self.on_key_press)

        # Reset the plot area and the stored lines
        self.reset()

    def reset(self):
        """Clears the figure, adds a new axis, resets the title, and clears all stored DataSet lines."""

        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.hasLegend = False
        self.title(Graph.default_title)
        # Lines is a list of DataSet objects. The user should take care to make
        # DataSet names unique, as there is no error checking done by Graph. 
        # If a DataSet line is deleted by its formal name, Graph will delete the
        # first line in the list that matches the name.
        self.lines = []

    def plot(self, x: np.array, y: np.array, name: str = None):
        """Plots x and y data on a Graph.

        Parameters
        ----------
        x : np.array
            The x axis values
        y : np.array
            The y axis values
        name : str, optional
            The name for this line (default = None)

        Raises
        ------
        ValueError
            If the shapes of x or y are different.
        """

        if x.shape == y.shape:
            dataset = DataSet(x, y, name)
            dataset.setObjectID(self.ax.plot(dataset.x, dataset.y))
            self.lines.append(dataset)
            self.legend()
            self.canvas.draw()
        else:
            raise ValueError("Error in required arguments for plotting.")        

    # Much help derived from https://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
    # self.lines is a list of DataSet objects. The user should take care to make
    # DataSet names unique, as there is no error checking done by Graph. 
    # If a DataSet line is deleted by its formal name, Graph will delete the
    # first line in the list that matches the name.
    def clear(self, value=None):
        if type(value) is int:
            self.ax.lines.remove(self.lines.pop(value).getObjectID())
        elif type(value) is str:
            for line in self.lines:
                if line.name == value:
                    self.ax.lines.remove(line.getObjectID())
                    self.lines.remove(line)
                    break
        else:
            self.reset()
        # Remove the lines that have been cleared from the legend.
        self.legend()
        self.canvas.draw()

    def legend(self, include: bool = None):
        if include == None:
            if self.hasLegend == True:
                include = True
            else:
                include = False
            
        if include == True:
            labels = []
            counter = 1
            for line in self.lines:
                if line.name is None:
                    labels.append("Line " + str(counter))
                    counter += 1
                else:
                    labels.append(line.name)
            self.ax.legend(labels).set_draggable(True)
            self.hasLegend = True
        else:
            self.ax.legend().remove()
            self.hasLegend = False
        self.canvas.draw()
    
    def linewidth(self, size: float):
        """
        Some line sizes:
        Ultrathin   Thin    Default     Thick   Ultrathick      Custom
        0.5         1.0     1.5         2.0     2.5             _._
        """
        for line in self.ax.lines:
            line.set_linewidth(size)
        self.canvas.draw()

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)

    def title(self, title: str):
        """Sets the window title and the graph title.
        
        Parameters
        ----------
        title : str
            The graph and window Title.
        """

        self.master.title(title)
        self.ax.set_title(title)
        self.canvas.draw()

    def xlabel(self, xlabel: str):
        """Sets the x-axis label.

        Parameters
        ----------
        xlabel : str
            The x-axis label.
        """

        self.ax.set_xlabel(xlabel)
        self.canvas.draw()

    def ylabel(self, ylabel: str):
        """Sets the y-axis label.

        Parameters
        ----------
        ylabel : str
            The y-axis label.
        """
        self.ax.set_ylabel(ylabel)
        self.canvas.draw()

    def close_windows(self):
        self.master.destroy()

def test(): 
    root = tk.Tk()

    app = Graph(tk.Toplevel(root))
    t = np.arange(0, 3, .01)
    app.plot(t, 2 * np.sin(2 * np.pi * t), "sin")
    t2 = np.arange(0, 6, .01)
    app.plot(t2, 5 * np.cos(2 * np.pi * t2), "cos")
    app.title("Frequency Response")
    app.xlabel("Time (s)")
    app.ylabel("Amplitude")
    #app.linewidth(0.5)
    app.legend(True)

    app2 = Graph(tk.Toplevel(root))
    app2.plot(t, 5 * np.cos(2 * np.pi * t))
    app2.title("New thing...")

    app.clear("cos")
    app2.clear()
    app2.plot(t, 5 * np.sin(2 * np.pi * t))
    app2.title("Back to sin")

    root.mainloop()

if __name__=="__main__":
    test()