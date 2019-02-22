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
        The Toplevel tkinter object that must exist for Graph to exist.
    menubar : tk.menu
        The tkinter menubar object for user operations.
    fig : matplotlib.figure.Figure
        The matplotlib figure object contained within Graph.
    canvas : matplotlib.backends.backend_tkagg.FigureCanvasTkAgg
        The matplotlib drawing canvas object contained within Graph.
    toolbar: matplotlib.backends.backend_tkagg.NavigationToolbar2Tk
        The matplotlib toolbar object contained within Graph.
    ax : matplotlib.axes.Axes
        The matplotlib axis upon which line and legend operations are performed.
    hasLegend : boolean
        A state variable used to maintain the legend's existence state between graph updates (default is false)
    lines : DataSet[]
        A list of DataSet objects containing the data points and their formal names.

    Methods
    -------
    reset()
        Clears the figure, adds a new axis, resets the title, and clears all stored DataSet lines.
    init_menu()
        Initializes all menu items and packs the object.
    on_key_press(event)
        Registers a key press event (default matplotlib keybindings are implemented).
    close_windows()
        Destroys the child tkinter object upon closing.
    plot(x=None, y=None, name=None)
        Plots x and y data on a Graph.
    clear(value)
        Deletes a stored DataSet value from the graph's self.lines DataSet objects list and removes 
        its line and legend from the plot.
    legend(include=None)
        Updates the legend's values and maintains its state. Can be used to activate/deactivate the legend.
    linewidth(size)
        Changes the linewidth of all plotted lines.
    title(title)
        Sets the window title and the graph title.
    xlabel(xlabel)
        Sets the x-axis label.
    ylabel(ylabel)
        Sets the y-axis label.
    """

    # Default window and plot title
    default_title = "Graph"

    #########################################################################
    #                                                                       #
    #                 GRAPH INITIALIZATION FUNCTIONS                        #
    #                                                                       #
    #########################################################################

    def __init__(self, master: tk.Toplevel):
        # The master tk object
        self.master = master
        self.menubar = tk.Menu(self.master)
        self.init_menu()
        self.master.config(menu=self.menubar)

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

    def init_menu(self):
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save")
        filemenu.add_command(label="Close", command=self.close_windows)
        self.menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_cascade(label="Delete line")
        self.menubar.add_cascade(label="Edit", menu=editmenu)

        appearancemenu = tk.Menu(self.menubar, tearoff=0)
        appearancemenu.add_checkbutton(label="Toggle legend")
        appearancemenu.add_command(label="Set title")
        appearancemenu.add_command(label="Set x label")
        self.menubar.add_cascade(label="Appearance", menu=appearancemenu)

        datamenu = tk.Menu(self.menubar, tearoff=0)
        datamenu.add_command(label="Save data as .mat")
        datamenu.add_command(label="Save data as .txt")
        datamenu.add_command(label="Save figure")
        self.menubar.add_cascade(label="Data", menu=datamenu)

    def on_key_press(self, event):
        """Registers a key press event (default matplotlib keybindings are implemented).

        Parameters
        ----------
        event : Event
            An event like a key press that is passed to the matplotlib key press handler.
        """

        #print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)

    def close_windows(self):
        """Destroys the child tkinter object upon closing."""

        self.master.destroy()

    #########################################################################
    #                                                                       #
    #               PLOTTING AND AXIS MANIPULATION FUNCTIONS                #
    #                                                                       #
    #########################################################################

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
    def clear(self, value=None):
        """Deletes a stored DataSet value from the graph's self.lines DataSet objects list and removes 
        its line and legend from the plot.

        The user should take care to make DataSet names unique, as there is no error checking done by Graph.

        Parameters
        ----------
        value : int or str
            If int, the line stored at the specified index is deleted.
            If str, the line with the specified name is deleted (no effect if it doesn't exist). Since no error
            checking is performed, Graph will delete the first line in the list whose string matches 'value'.
        """

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
        """Updates the legend's values and maintains its state.

        Parameters
        ----------
        include : bool, optional
            If not specified, default behavior is to maintain the legend's present state (self.hasLegend).
            If true, a draggable legend is placed onto the Graph.
            If false, the legend is turned off.
        """
        
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
            if self.hasLegend == True: # Prevents error messages from removing nonexisting legend
                self.ax.legend().remove()
            self.hasLegend = False
        self.canvas.draw()
    
    def linewidth(self, size: float):
        """Changes the linewidth of all plotted lines.

        Some suggested line sizes:
        Ultrathin   Thin    Default     Thick   Ultrathick      Custom
        0.5         1.0     1.5         2.0     2.5             _._

        Parameters
        ----------
        size : float
            A floating point value of the thickness to use.
        """
        for line in self.ax.lines:
            line.set_linewidth(size)
        self.canvas.draw()

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