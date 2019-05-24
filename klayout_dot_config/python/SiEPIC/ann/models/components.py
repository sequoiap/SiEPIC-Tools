"""
components.py

Author: Sequoia Ploeg
Modified on 5/23/2019

Dependencies:
- importlib
    Dynamically imports the installed component models.
- jsons
    Similar to GSON in Java, serializes and deserializes custom models.
    API: https://jsons.readthedocs.io/en/latest/index.html
- json
    Allows for writing and reading from JSON files.

This file loads all components within the models package. It also provides 
netlist capabilities, formatting all components as JSON.
"""


"""
This is where you should list all installed components from which you plan to get 
s-parameters. In addition to listing the modules here, make sure to list the 
relevant modules within each component class below, too, under _simulation_model.
"""
INSTALLED_COMPONENTS = [
    'wg_ann',
    'wg1550_lumerical',
    'ebeam_bdc_te1550',
]

"""
BEGIN DO NOT ALTER
"""
import sys
from importlib import import_module
import jsons
import json

LOADED_MODELS = {}

try:
    for component in INSTALLED_COMPONENTS:
        mod = import_module('.' + component, 'SiEPIC.ann.models')
        LOADED_MODELS[component] = mod.Model
except:
    print("SiEPIC-Tools is not in the current namespace.")
    for component in INSTALLED_COMPONENTS:
        mod = import_module(component)
        LOADED_MODELS[component] = mod.Model
"""
END DO NOT ALTER
"""

class Component:
    """This class represents an arbitrary component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This is the base class for all netlist components. All components have a type, a
    list of nets, x/y layout positions, and a list of simulation models from which the
    component in question could retrieve s-parameters.

    All class extensions should provide additional data members with type hints and 
    default values if necessary.

    Class Attributes
    ----------------
    _simulation_models : dict
        A dictionary of installed models (packages) from which this component could 
        retrieve s-parameters. This is a class attribute, and is not stored at the instance 
        level or in JSON output. It's format is {'[Human Readable Name]': '[Model Location]'}.
    # _selected_model : str
    #     A key from the _simulation_models dictionary.

    Attributes
    ----------
    component_type : str
        The name of the component type.
    nets : list of ints
        A list of all port connections (required to be integers).
    lay_x : float
        The x-position of the component in the overall layout.
    lay_y : float
        The y-position of the component in the overall layout.
    """
    component_type: str = None
    nets: list = []
    lay_x: float = 0
    lay_y: float = 0
    _simulation_models: dict = {}

    @staticmethod
    def setup(obj):
        obj._selected_model = next(iter(obj._simulation_models)) if obj._simulation_models else None
        obj._model_ref = LOADED_MODELS[obj._simulation_models[obj._selected_model]] if obj._selected_model else None

    def __init__(self, *args, **kwargs):
        """Initializes a Component dataclass.

        Parameters
        ----------
        nets : list of ints
            A list of all port connections (required to be integers).
        lay_x : float
            The x-position of the component in the overall layout.
        lay_y : float
            The y-position of the component in the overall layout.
        """
        self.component_type = type(self).__name__
        if 'nets' in kwargs:
            self.nets = kwargs.get('nets')
        if 'lay_x' in kwargs:
            self.lay_x = kwargs.get('lay_x')
        if 'lay_y' in kwargs:
            self.lay_y = kwargs.get('lay_y')

    @classmethod
    def set_model(cls, key):
        cls._selected_model = key
        cls._model_ref = LOADED_MODELS[cls._simulation_models[cls._selected_model]] if cls._selected_model else None

    def __str__(self):
        return 'Object::' + str(self.__dict__)




class ebeam_wg_integral_1550(Component):
    """This class represents a waveguide component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    length : float
        Total waveguide length.
    width : float
        Designed waveguide width.
    height : float
        Designed waveguide height.
    """
    length: float = 0
    width: float = 500e-9
    height: float = 220e-9
    radius: float = 0
    points: list = []

    _simulation_models = {
        'ANN': 'wg_ann',
        'Lumerical': 'wg1550_lumerical',
    }

    def __init__(self, *args, **kwargs):
        """Initializes a ebeam_wg_integral_1550 dataclass, which inherits from Component.

        Parameters
        ----------
        length : float
            Total waveguide length.
        width : float
            Designed waveguide width.
        height : float
            Designed waveguide height.
        points : list of tuples
        """
        super().__init__(*args, **kwargs)
        if 'length' in kwargs:
            self.length = kwargs.get('length')
        if 'width' in kwargs:
            self.width = kwargs.get('width')
        if 'height' in kwargs:
            self.height = kwargs.get('height')
        if 'points' in kwargs:
            self.points = kwargs.get('points')




class ebeam_bdc_te1550(Component):
    """This class represents a bidirectional coupler component in the netlist. All attributes 
    can be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    Inherited
    """
    _simulation_models = {
        'EBeam BDC': 'ebeam_bdc_te1550',
    }
    
    def __init__(self, *args, **kwargs):
        """Initializes a ebeam_bdc_te1550 dataclass, which inherits from Component.

        Parameters
        ----------
        Inherited
        """
        super().__init__(*args, **kwargs)




class ebeam_gc_te1550(Component):
    """This class represents a grating coupler component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    Inherited
    """
    _simulation_models = {
        
    }
    
    def __init__(self, *args, **kwargs):
        """Initializes a ebeam_gc_te1550 dataclass, which inherits from Component.

        Parameters
        ----------
        Inherited
        """
        super().__init__(*args, **kwargs)




class ebeam_y_1550(Component):
    """This class represents a Y-branch component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    Inherited
    """
    _simulation_models = {
        
    }
    
    def __init__(self, *args, **kwargs):
        """Initializes a ebeam_y_1550 dataclass, which inherits from Component.

        Parameters
        ----------
        Inherited
        """
        super().__init__(*args, **kwargs)




class ebeam_terminator_te1550(Component):
    """This class represents a terminator component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    Inherited
    """
    _simulation_models = {
        
    }
    
    def __init__(self, *args, **kwargs):
        """Initializes a ebeam_terminator_te1550 dataclass, which inherits from Component.

        Parameters
        ----------
        Inherited
        """
        super().__init__(*args, **kwargs)




class ebeam_dc_halfring_te1550(Component):
    """This class represents a half-ring component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    Inherited
    """
    _simulation_models = {
        
    }
    
    def __init__(self, *args, **kwargs):
        """Initializes a ebeam_dc_halfring_te1550 dataclass, which inherits from Component.

        Parameters
        ----------
        Inherited
        """
        super().__init__(*args, **kwargs)




"""

IMPLEMENTATION CODE BELOW, PROCEED WITH CAUTION!

"""

def strToSci(str):
    '''
    local function to convert strings written in Klayout's 
    exponential notation into floats
    Args:
        str (str): string to convert to float
    Returns:
        float representation of the input string
    '''

    ex = str[-1]
    base = float(str[:-1])
    if(ex == 'm'):
        return base * 1e-3
    elif(ex == 'u'):
        return base * 1e-6
    elif(ex == 'n'):
        return base * 1e-9
    else:
        return float(str(base) + ex)

class Parser:
    '''
    The Parser class reads a netlist generated by the SiEPIC toolbox and uses 
    various classes which inherit from 'models.components.Component' to create an 
    object based model of a photonic circuit. 
    
    Each derived class is connected to a component model in 'models' that exposes a 
    'get_s_params' method with its appropriate arguments to the derived model. These 
    s_params are the s-matrices of the component, which are then used to simulate the 
    circuit's transmission behavior.

    Attributes
    ----------
    component_list : list
        A list of objects derived from 'models.components.Component' representing the
        photonic circuit.
    nports : int
        A counter keeping track of the total number of nets in the circuit (0-indexed).

    Methods
    -------
    parse_file(filepath)
        Parses through the netlist to identify components and organize them into objects.
        Objects are connected with their data models, allowing them to retrieve any
        available parameters.
    _parse_line(line_elements)
        Reads the elements on a line of the netlist (already delimited before passed to
        _parse_line) and creates the appropriate object. Appends the newly created object
        to the Parser's component_list.

    # 'cascadeCells' takes the cellList gathered by 'parseFile' and cascades all the s-matrices together
    # using scikit-rf's 'connect_s' and 'innerconnect_s' functions, deleting already connected Cells as
    # it goes. The result is a single Cell object with an s-matrix representing the cascaded circuit
    '''

    def __init__(self):
        '''
        Initializes a Parser and creates a structure to hold a list of components
        and count the number of nets in the circuit (0-indexed).
        '''
        self.component_list = []
        self.nports = 0


    def parse_file(self, filepath: str):
        '''
        reads the netlist file and calls 'parseCell' to create Cell objects from 
        the netlist entries
        Args:
            none
            self.filepath is the needed path to the netlist
        Returns
            none
            the call to 'parseCell' will add a new Cell to self.cellList
        '''

        with open(filepath) as fid:
            text = fid.read()
            return self.parse_text(text)
        #     lines = fid.readlines()
        #     for line in lines:
        #         elements = line.split()
        #         if len(elements) > 0:
        #             if (".ends" in elements[0]):
        #                 break
        #             elif ("." in elements[0]) or ("*" in elements[0]):
        #                 continue
        #             else:
        #                 self._parse_line(elements)
        # return self.component_list

    def parse_text(self, text: str):
        lines = text.splitlines()
        for line in lines:
                elements = line.split()
                if len(elements) > 0:
                    if (".ends" in elements[0]):
                        break
                    elif ("." in elements[0]) or ("*" in elements[0]):
                        continue
                    else:
                        self._parse_line(elements)
        return self.component_list
        

    def _parse_line(self, line_elements: list):
        '''
        Parses a line from the netlist, already split into individual elements, and 
        converts it into a new Component object.
        
        Parameters
        ----------
        line_elements : list
            A list of all the elements on a line (already split by some delimiter).
        '''

        component = None
        nets = []
        for item in line_elements[1:]:
            if "N$" in item:
                net = str(item).replace("N$", '')
                nets.append(net)
                if int(net) > self.nports:
                    self.nports = int(net)
                continue
            elif component is None:
                component = create_component_by_name(item)
            elif "lay_x=" in item:
                component.lay_x = float(str(item).replace("lay_x=", ''))
            elif "lay_y=" in item:
                component.lay_y = float(str(item).replace("lay_y=", ''))
            elif "radius=" in item:
                component.radius = float(str(item).replace("radius=", ''))
            elif "wg_length=" in item:
                lenth = str(item).replace("wg_length=", '')
                component.length = strToSci(lenth)
            elif "wg_width=" in item:
                width = str(item).replace("wg_width=", '')
                component.width = strToSci(width)
            elif "points=" in item:
                # The regex, in case you ever need it: /(\[[\d]+[\,][\d]+\])/g
                points = str(item).replace("points=", '')
                points = points.replace("\"[[", '')
                points = points.replace("]]\"", '')
                point_list = points.split('],[')
                for point in point_list:
                    out = point.split(',')
                    component.points.append((float(out[0]), float(out[1])))
        component.nets = nets
        self.component_list.append(component)


    # def cascadeCells(self):
    #     '''
    #     For each pin in the circuit, the s-matrices of the Cells containing that pin are cascaded
    #     using scikit-rf funtions. 'innerconnect_s' if the two occurances of the pin are in the
    #     same Cell, 'connect_s' if they are in two different cells

    #     For a pin:
    #     * 'findPortMatch' is called to find where the two occurances of the pin are
    #     * If they are in the same Cell, use 'innerconnect_s' to cascade the s-matrices and delete the
    #         connected ports from the Cell's port list
    #     * If they are in different Cells, create a new Cell object and let its s-matrix be the result 
    #         of 'connect_s' for the two Cells. Delete the two Cells from the cellList

    #     Repeat this process until all pins have been connected

    #     One Cell will remain in the cellList. Its s-matrix represents the transmission behavior of the
    #     circuit as a whole
    #     '''

    #     if self.nports == 0:
    #         return
    #     for n in range(0, self.nports + 1):
    #         ca, ia, cb, ib = findPortMatch(str(n), self.cellList)

    #         #if pin occurances are in the same Cell
    #         if ca == cb:
    #             self.cellList[ca].s = rf.innerconnect_s(self.cellList[ca].s, ia, ib)
    #             del self.cellList[ca].p[ia]
    #             if ia < ib:
    #                 del self.cellList[ca].p[ib-1]
    #             else:
    #                 del self.cellList[ca].p[ib]

    #         #if pin occurances are in different Cells
    #         else:
    #             d = Cell()
    #             d.f = self.cellList[0].f
    #             d.s = rf.connect_s(self.cellList[ca].s, ia, self.cellList[cb].s, ib)
    #             del self.cellList[ca].p[ia]
    #             del self.cellList[cb].p[ib]
    #             d.p = self.cellList[ca].p + self.cellList[cb].p
    #             del self.cellList[ca]
    #             if ca < cb:
    #                 del self.cellList[cb-1]
    #             else:
    #                 del self.cellList[cb]
    #             self.cellList.append(d)

# Finish setting all class variables for component subclasses
comp_subclasses = [class_ for class_ in Component.__subclasses__()]
for class_ in comp_subclasses:
    class_.setup(class_)

def create_component_by_name(component_name: str):
    return getattr(sys.modules[__name__], component_name)()

def netlist_lumerical_to_json(filename):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print(os.getcwd())
    components = Parser().parse_file(filename)
    output = jsons.dump(components, verbose=True, strip_privates=True)
    with open('netlist.json', 'w') as outfile:
        json.dump(output, outfile, indent=2)


import os
if __name__ == "__main__":
    w1 = ebeam_wg_integral_1550(length=50e-6, width=500.05129e-9, height=220)
    w2 = ebeam_wg_integral_1550(nets=[2,3], length=150e-6, width=499.5129e-9, height=220)
    items = []
    items.append(w1)
    items.append(w2)
    output = jsons.dump(items, verbose=True, strip_privates=True)
    with open('data.json', 'w') as outfile:
        json.dump(output, outfile, indent=2)
    data = None
    with open('data.json') as jsonfile:
        data = json.load(jsonfile)
    inputstr = jsons.load(data)
    # os.remove('data.json')
    LOADED_MODELS[ebeam_wg_integral_1550._simulation_models['Lumerical']].about()

    netlist_lumerical_to_json('netlist.txt')