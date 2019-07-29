__all__ = [
    'setup',
    'netlist',
    'single_port_simulation',
    'monte_carlo_simulation',
    # 'multi_port_simulation',
    'settings_gui',
    'config',
]

from . import *

import atexit
import configparser
from importlib import import_module
import os
import SiEPIC_Simphony.config as configure

def on_open():
    print('Simphony Python Integration (CamachoLab)')
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.ini"))
        selections = config['MODEL_SELECT']

        for item in selections:
            configure.set_model(item, selections[item])
    except:
        print("Persistent settings could not be read.")

def on_close():
    config = configparser.ConfigParser()
    config['MODEL_SELECT'] = {}
    selections = config['MODEL_SELECT']

    for k, v in configure.selected_models.items():
        selections[k] = v.component_type

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.ini"), 'w') as configfile:
        config.write(configfile)
    print("Simphony Integration Closed")

on_open()

atexit.register(on_close)
