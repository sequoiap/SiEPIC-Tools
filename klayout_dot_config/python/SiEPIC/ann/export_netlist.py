import pya
import SiEPIC.extend as se
import SiEPIC.core as cor

def spice_netlist_export(self, verbose=False, opt_in_selection_text=[]):
    '''
    This function gathers information from the current top cell in Klayout into a netlist
    for a photonic circuit. This netlist is used in simulations.

    Most of this function comes from a function in 'lukasc-ubc/SiEPIC-Tools/klayout_dot_config/python/SiEPIC/extend.py' which does the
    same thing. This function has parts of that one removed because they were not needed for our toolbox.
    '''

    import SiEPIC
    from SiEPIC import _globals
    from time import strftime
    from SiEPIC.utils import eng_str

    from SiEPIC.utils import get_technology
    TECHNOLOGY = get_technology()
    if not TECHNOLOGY['technology_name']:
        v = pya.MessageBox.warning("Errors", "SiEPIC-Tools requires a technology to be chosen.  \n\nThe active technology is displayed on the bottom-left of the KLayout window, next to the T. \n\nChange the technology using KLayout File | Layout Properties, then choose Technology and find the correct one (e.g., EBeam, GSiP).", pya.MessageBox.Ok)
        return 'x', 'x', 0, [0]
    # get the netlist from the entire layout
    nets, components = self.identify_nets()

    if not components:
        v = pya.MessageBox.warning("Errors", "No components found.", pya.MessageBox.Ok)
        return 'no', 'components', 0, ['found']

    if verbose:
        print("* Display list of components:")
        [c.display() for c in components]
        print("* Display list of nets:")
        [n.display() for n in nets]

    text_main = '* Spice output from KLayout SiEPIC-Tools v%s, %s.\n\n' % (
        SiEPIC.__version__, strftime("%Y-%m-%d %H:%M:%S"))
    text_subckt = text_main
        
    circuit_name = self.name.replace('.', '')  # remove "."
    if '_' in circuit_name[0]:
        circuit_name = ''.join(circuit_name.split('_', 1))  # remove leading _

    KLayoutInterconnectRotFlip = \
    {(0, False): [0, False],
    (90, False): [270, False],
    (180, False): [180, False],
    (270, False): [90, False],
    (0, True): [180, True],
    (90, True): [90, True],
    (180, True): [0, True],
    (270, True): [270, False]}

    # create the top subckt:
    #text_subckt += '.subckt %s%s%s\n' % (circuit_name, electricalIO_pins, opticalIO_pins)
    # assign MC settings before importing netlist components
    text_subckt += '.param MC_uniformity_width=0 \n'
    text_subckt += '.param MC_uniformity_thickness=0 \n'
    text_subckt += '.param MC_resolution_x=100 \n'
    text_subckt += '.param MC_resolution_y=100 \n'
    text_subckt += '.param MC_grid=10e-6 \n'
    text_subckt += '.param MC_non_uniform=99 \n'

    ioports = -1
    for c in components:
        # optical nets: must be ordered electrical, optical IO, then optical
        nets_str = ''
        for p in c.pins:
            if p.type == _globals.PIN_TYPES.ELECTRICAL:
                nets_str += " " + c.component + '_' + str(c.idx) + '_' + p.pin_name
        for p in c.pins:
            if p.type == _globals.PIN_TYPES.OPTICALIO:
                nets_str += " N$" + str(ioports)
                ioports -= 1
        #pinIOtype = any([p for p in c.pins if p.type == _globals.PIN_TYPES.OPTICALIO])
        for p in c.pins:
            if p.type == _globals.PIN_TYPES.OPTICAL:
                if p.net.idx != None:
                    nets_str += " N$" + str(p.net.idx)
                #if p.net.idx != None:
                #    nets_str += " N$" + str(p.net.idx)
                else:
                    nets_str += " N$" + str(ioports)
                    ioports -= 1

        trans = KLayoutInterconnectRotFlip[(c.trans.angle, c.trans.is_mirror())]

        flip = ' sch_f=true' if trans[1] else ''
        if trans[0] > 0:
            rotate = ' sch_r=%s' % str(trans[0])
        else:
            rotate = ''

        # Check to see if this component is an Optical IO type.
        pinIOtype = any([p for p in c.pins if p.type == _globals.PIN_TYPES.OPTICALIO])

        ignoreOpticalIOs = False
        if ignoreOpticalIOs and pinIOtype:
            # Replace the Grating Coupler or Edge Coupler with a 0-length waveguide.
            component1 = "ebeam_wg_strip_1550"
            params1 = "wg_length=0u wg_width=0.500u"
        else:
            component1 = c.component
            params1 = c.params

        text_subckt += ' %s %s %s ' % (component1.replace(' ', '_') +
                                       "_" + str(c.idx), nets_str, component1.replace(' ', '_'))
        if c.library != None:
            text_subckt += 'library="%s" ' % c.library
        x, y = c.Dcenter.x, c.Dcenter.y
        text_subckt += '%s lay_x=%s lay_y=%s\n' % \
            (params1, eng_str(x * 1e-6), eng_str(y * 1e-6))

    text_subckt += '.ends %s\n\n' % (circuit_name)
    return text_subckt, text_main

#extension of pya.Cell class to include this function
pya.Cell.spice_netlist_export = spice_netlist_export

def main():
    '''
    main function that prints the netlist for the active top cell
    used for testing purposes
    '''

    cell = pya.Application.instance().main_window().current_view().active_cellview().cell
    text_subckt, text_main = cell.spice_netlist_export(verbose=True)
    cell.spice_netlist_export()
    print("***TEXT_SUBCKT***")
    print(text_subckt)
    print("***TEXT_MAIN***")
    print(text_main)
  
if __name__ == "__main__":
    main()

