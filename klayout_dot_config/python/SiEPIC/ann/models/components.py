"""
components.py

"""

INSTALLED_COMPONENTS = [
    '.wg_ann',
    '.wg1550_lumerical',
]


#######################################
#                                     #
#           IMPLEMENTATION            #
#                                     #
#######################################

from importlib import import_module
import jsons
from enum import Enum

LOADED_MODELS = {}

for component in INSTALLED_COMPONENTS:
    mod = import_module(component, 'SiEPIC.ann.models')
    LOADED_MODELS[component.replace('.', '')] = mod.Model

# for key, val in LOADED_MODELS.items():
#     print(key, val)

class Component:
    """This class represents an arbitrary component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This is the base class for all netlist components. All components have a type and a
    list of ports.

    Attributes
    ----------
    compType : str
        The name of the component type.
    ports : list of ints
        A list of all port connections (required to be integers).
    """
    compType: str
    ports: list

    def __init__(self, *args, **kwargs):
        """Initializes a Component dataclass.

        Parameters
        ----------
        compType : str
            The name of the component type.
        ports : list of ints
            A list of all port connections (required to be integers).
        """
        if 'compType' in kwargs:
            self.compType = kwargs.get('compType')
        if 'ports' in kwargs:
            self.ports = kwargs.get('ports')

    def __repr__(self):
        return str(self.__dict__)

class Waveguide(Component):
    """This class represents a waveguide component in the netlist. All attributes can
    be initialized as keyword arguments in the __init__ function.

    This class inherits from Component and inherits all of its data members.

    Attributes
    ----------
    compType : str
        The name of the component type.
    ports : list of ints
        A list of all port connections (required to be integers).
    length : float
        Total waveguide length.
    width : float
        Designed waveguide width.
    height : float
        Designed waveguide height.
    """
    length: float
    width: float
    height: float

    def __init__(self, *args, **kwargs):
        """Initializes a Waveguide dataclass, which inherits from Component.

        Parameters
        ----------
        compType : str
            The name of the component type.
        ports : list of ints
            A list of all port connections (required to be integers).
        length : float
            Total waveguide length.
        width : float
            Designed waveguide width.
        height : float
            Designed waveguide height.
        """
        super().__init__(*args, **kwargs)
        if 'length' in kwargs:
            self.length = kwargs.get('length')
        if 'width' in kwargs:
            self.width = kwargs.get('width')
        if 'height' in kwargs:
            self.height = kwargs.get('height')

class CompType(Enum):
    '''
    Enum listing of all available component types.

    Name, value pairs comprise of the component type as shown on the netlist, paired with
    its dataclass model as the value.
    '''

    ebeam_bdc_te1550 = Component
    ebeam_dc_halfring_te1550 = Component
    ebeam_gc_te1550 = Component
    ebeam_y_1550 = Component
    ebeam_terminator_te1550 = Component
    ebeam_wg_integral_1550 = Waveguide

def component_factory(JSONobj: str):
    """Creates one of the objects that inherits from Component (based on the value of compType)
    given the object's JSON representation.

    Parameters
    ----------
    JSONobj : str
        The string representation of the JSON object.
    """
    instance = jsons.load(JSONobj, Component)
    
    for type_ in CompType:
        if instance.compType == type_.name:
            return jsons.load(JSONobj, type_.value)

if __name__ == "__main__":
    c = Waveguide(compType='ebeam_wg_integral_1550', ports=[1,2], length=50, width=60, height=70)
    dumped = jsons.dump(c)
    obj = component_factory(dumped)