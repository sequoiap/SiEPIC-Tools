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
        waveguideLengthDelta = 0
        # Get s parameters and frequencies (generates the netlist, too).
        self.s_matrix, self.frequency = gs.getSparams(waveguideWidth, waveguideThickness, waveguideLengthDelta)
        self.ports = gs.getPorts(waveguideWidth, waveguideThickness, waveguideLengthDelta)

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

import matplotlib.pyplot as plt
from scipy.io import savemat
import time

DEF_NUM_SIMS = 10
DEF_MU_WIDTH = 0.5
DEF_SIGMA_WIDTH = 0.005
DEF_MU_THICKNESS = 0.22
DEF_SIGMA_THICKNESS = 0.002
DEF_MU_LENGTH = 0
DEF_SIGMA_LENGTH = 0
DEF_DPIN = 1
DEF_DPOUT = 0
DEF_SAVEDATA = True
DEF_DISPTIME = True
DEF_FILENAME = "monte_carlo.mat"

def monte_carlo_sim(num_sims=DEF_NUM_SIMS, mu_width=DEF_MU_WIDTH, sigma_width=DEF_SIGMA_WIDTH, mu_thickness=DEF_MU_THICKNESS,
    sigma_thickness=DEF_SIGMA_THICKNESS, mu_length=DEF_MU_LENGTH, sigma_length=DEF_SIGMA_LENGTH, dpin=DEF_DPIN, dpout=DEF_DPOUT, 
    saveData=False, filename=None, dispTime=False, printer=None):

    # optional timer
    start = time.time()

    # random distribution for width
    random_width = np.random.normal(mu_width, sigma_width, num_sims)

    # random distribution for thickness
    random_thickness = np.random.normal(mu_thickness, sigma_thickness, num_sims)

    # random distribution for length change
    random_deltaLength = np.random.normal(mu_length, sigma_length, num_sims)

    # run simulation with mean width and thickness
    mean_s, frequency = gs.getSparams(mu_width, mu_thickness, 0)
    results_shape = np.append(np.asarray([num_sims]), mean_s.shape)
    results = np.zeros([dim for dim in results_shape], dtype='complex128')

    # run simulations with varied width and thickness
    for sim in range(num_sims):
        #random_deltaLength[sim]
        results[sim, :, :, :] = gs.getSparams(random_width[sim], random_thickness[sim], random_deltaLength[sim])[0]
        if ((sim % 10) == 0) and dispTime:
            print(sim)

    # rearrange matrix so matrix indices line up with proper port numbers
    p = gs.getPorts(random_width[0], random_thickness[0], 0)
    p = [int(i) for i in p]
    rp = copy.deepcopy(p)
    rp.sort(reverse=True)
    # TODO: Remove this duplicate code. It's been implemented once in the Simulation.py class
    concatinate_order = [p.index(i) for i in rp]
    temp_res = copy.deepcopy(results)
    temp_mean = copy.deepcopy(mean_s)
    re_res = np.zeros(results_shape, dtype=complex)
    re_mean = np.zeros(mean_s.shape, dtype=complex)
    i=0
    for idx in concatinate_order:
        re_res[:,:,i,:]  = temp_res[:,:,idx,:]
        re_mean[:,i,:] = temp_mean[:,idx,:]
        i += 1
    temp_res = copy.deepcopy(re_res)
    temp_mean = copy.deepcopy(re_mean)
    i=0
    for idx in concatinate_order:
        re_res[:,:,:,i] = temp_res[:,:,:,idx]
        re_mean[:,:,i] = temp_mean[:,:,idx]
        i+= 1    
    results = copy.deepcopy(re_res)
    mean_s = copy.deepcopy(re_mean)

    # print elapsed time if dispTime is True
    stop = time.time()
    if dispTime and printer:
        printer('Total simulation time: ' + str(stop-start) + ' seconds')

    # save MC simulation results to matlab file
    if saveData == True:
        savemat(filename, {'freq':frequency, 'results':results, 'mean':mean_s})

    plt.figure(1)
    for i in range(num_sims):
        plt.plot(frequency, 10*np.log10(abs(results[i, :, dpin, dpout])**2), 'b', alpha=0.1)
    plt.plot(frequency,  10*np.log10(abs(mean_s[:, dpin, dpout])**2), 'k', linewidth=0.5)
    title = 'Monte Carlo Simulation (' + str(num_sims) + ' Runs)'
    plt.title(title)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain (dB)')
    plt.draw()
    plt.show()