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
import json
from enum import Enum

LOADED_MODELS = {}

for component in INSTALLED_COMPONENTS:
    mod = import_module(component, 'SiEPIC.ann.models')
    LOADED_MODELS[component.replace('.', '')] = mod.Model

# for key, val in LOADED_MODELS.items():
#     print(key, val)

class CompType(Enum):
    '''
    Enum listing of all available component types.
    '''

    BDC = 'ebeam_bdc_te1550'
    DC = 'ebeam_dc_halfring_te1550'
    GC = 'ebeam_gc_te1550'
    YB = 'ebeam_y_1550'
    TR = 'ebeam_terminator_te1550'
    WG = 'ebeam_wg_integral_1550'

class Component(dict):
    def __init__(self, compType=NotImplemented):
        self.compType = compType
        self.ports = []

class Waveguide(Component):
    def __init__(self):
        self.length = 0
        self.width = 0
        self.height = 0

def parse_component(obj, verbose=False):
    if verbose:
        print(obj['type'])

    if obj['type'] == "Waveguide":
        component = Waveguide()
    else:
        component = Component()
    component.__dict__.update(obj)
    return component

s = '[{ "type" : "Waveguide", "length" : 50, "width" : 500, "height" : 220 }, { "type" : "ybranch", "ports" : 50 }]'
o = json.loads(s, object_hook=parse_component)

o1 = Waveguide()
o1.compType = CompType.WG
o2 = Component()
o2.compType = CompType.BDC

objs = [o1, o2]
print(json.dumps(objs))