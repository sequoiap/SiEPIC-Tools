import pya
import simphony
import SiEPIC_Simphony

def registerMenuItems():
    import os
    #from . import scripts, examples, lumerical, install

    global SIMPHONY_ACTIONS
    count = len(SIMPHONY_ACTIONS)
    menu = pya.Application.instance().main_window().menu()
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "files", "light.png")
    
    import sys
    
    s1 = "simphony_menu"
    if not(menu.is_menu(s1)):
        menu.insert_menu("help_menu", s1, "Simphony %s" % simphony.__version__)

    #s2 = "simulations"
    #if not(menu.is_menu(s1 + "." + s2)):
    #    menu.insert_menu(s1 + ".end", s2, "Waveguides")
    
    if not(menu.is_menu("@toolbar.cir_sim_simphony")):
        SIMPHONY_ACTIONS.append(pya.Action())
        menu.insert_item("@toolbar.end", "cir_sim_simphony", SIMPHONY_ACTIONS[count])
    SIMPHONY_ACTIONS[count].title = "Simphony\nSimulation"
    SIMPHONY_ACTIONS[count].on_triggered(SiEPIC_Simphony.single_port_simulation.circuit_analysis)
    SIMPHONY_ACTIONS[count].icon = path
    count += 1

if __name__ == "__main__":
    registerMenuItems()