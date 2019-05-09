import numpy as np
import copy

from SiEPIC.ann import getSparams as gs
from SiEPIC.ann import NetlistDiagram

class MathPrefixes:
    TERA = 1e12
    NANO = 1e-9
    c = 299792458

class Simulation:
    def __init__(self):
        # parameters for generating waveguide s parameters
        waveguideWidth = 0.5
        waveguideThickness = 0.22
        # Get s parameters and frequencies (generates the netlist, too).
        self.s_matrix, self.frequency = gs.getSparams(waveguideWidth, waveguideThickness, regenerate_netlist=True)
        self.ports = gs.getPorts(waveguideWidth, waveguideThickness)

        self.external_port_list, self.external_components = NetlistDiagram.getExternalPortList()
        self._rearrangeSMatrix()
        return

    def _rearrangeSMatrix(self):
        ports = [int(i) for i in self.ports]
        reordered = copy.deepcopy(ports)
        reordered.sort(reverse = True)
        concatenate_order = [ports.index(i) for i in reordered]
        new_s = copy.deepcopy(self.s_matrix)
        reordered_s = np.zeros(self.s_matrix.shape, dtype=complex)

        i = 0
        for idx in concatenate_order:
            reordered_s[:,i,:] = new_s[:,idx,:]
            i += 1
        new_s = copy.deepcopy(reordered_s)
        i = 0
        for idx in concatenate_order:
            reordered_s[:,:,i] = new_s[:,:,idx]
            i += 1
        
        self.s_matrix = copy.deepcopy(reordered_s)

    def frequencyToWavelength(self, frequency):
        return MathPrefixes.c / frequency

    def getMagnitudeByFrequencyTHz(self, fromPort, toPort):
        print("From", fromPort, "to", toPort)
        freq = np.divide(self.frequency, MathPrefixes.TERA)
        mag = abs(self.s_matrix[:,fromPort,toPort])**2
        return freq, mag
    
    def getMagnitudeByWavelengthNm(self, fromPort, toPort):
        wl = self.frequencyToWavelength(self.frequency) / MathPrefixes.NANO
        mag = abs(self.s_matrix[:,fromPort,toPort])**2
        return wl, mag

    def getPhaseByFrequencyTHz(self, fromPort, toPort):
        freq = np.divide(self.frequency, MathPrefixes.TERA)
        phase = np.rad2deg(np.unwrap(np.angle(self.s_matrix[:,fromPort,toPort])))
        return freq, phase

    def getPhaseByWavelengthNm(self, fromPort, toPort):
        wl = self.frequencyToWavelength(self.frequency) / MathPrefixes.NANO
        phase = np.rad2deg(np.unwrap(np.angle(self.s_matrix[:,fromPort,toPort])))
        print(wl, phase)
        return wl, phase

    def exportSMatrix(self):
        return self.s_matrix, self.frequency

