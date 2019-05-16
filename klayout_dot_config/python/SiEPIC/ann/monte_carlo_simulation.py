import pya
import sys
import os
import numpy as np
import copy
import matplotlib.pyplot as plt
from scipy.stats import kde
from SiEPIC.ann import getSparams as gs
from SiEPIC.ann import cascade_netlist as cn
from scipy.io import savemat
from scipy.signal import find_peaks
import time

import tkinter as tk
from tkinter import filedialog
import os

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

class MonteCarloGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.title("Monte Carlo Simulation")

        padx = 5
        pady = 5

        bbox = tk.Frame(padx=padx, pady=pady)
        bbox.pack()

        sim_group = tk.LabelFrame(bbox, text="Simulation", padx=padx, pady=pady)
        sim_group.pack(fill=tk.BOTH)
        tk.Label(sim_group, text="Number of simulations: ").pack(side=tk.LEFT)
        self.num_sims = tk.Entry(sim_group)
        self.num_sims.pack(side=tk.LEFT)
        self.num_sims.insert(0, str(DEF_NUM_SIMS))
        
        var_group = tk.Frame(bbox)
        var_group.pack(fill=tk.BOTH)

        stdev_group = tk.LabelFrame(var_group, text="Standard Deviations", padx=padx, pady=pady)
        stdev_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        tk.Label(stdev_group, text="Width:").grid(row=0, column=0, sticky=tk.W)
        self.sigma_width = tk.Entry(stdev_group)
        self.sigma_width.grid(row=0, column=1)
        self.sigma_width.insert(0, str(DEF_SIGMA_WIDTH))
        tk.Label(stdev_group, text="Thickness:").grid(row=1, column=0, sticky=tk.W)
        self.sigma_thickness = tk.Entry(stdev_group)
        self.sigma_thickness.grid(row=1, column=1)
        self.sigma_thickness.insert(0, str(DEF_SIGMA_THICKNESS))
        tk.Label(stdev_group, text="Length:").grid(row=2, column=0, sticky=tk.W)
        self.sigma_length = tk.Entry(stdev_group)
        self.sigma_length.grid(row=2, column=1)
        self.sigma_length.insert(0, str(DEF_SIGMA_LENGTH))

        mean_group = tk.LabelFrame(var_group, text="Means", padx=padx, pady=pady)
        mean_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        tk.Label(mean_group, text="Width (um):").grid(row=0, column=0, sticky=tk.W)
        self.mean_width = tk.Entry(mean_group)
        self.mean_width.grid(row=0, column=1)
        self.mean_width.insert(0, str(DEF_MU_WIDTH))
        tk.Label(mean_group, text="Thickness (um):").grid(row=1, column=0, sticky=tk.W)
        self.mean_thickness = tk.Entry(mean_group)
        self.mean_thickness.grid(row=1, column=1)
        self.mean_thickness.insert(0, str(DEF_MU_THICKNESS))
        tk.Label(mean_group, text="Length (um):").grid(row=2, column=0, sticky=tk.W)
        self.mean_length = tk.Entry(mean_group)
        self.mean_length.grid(row=2, column=1)
        self.mean_length.insert(0, str(DEF_MU_LENGTH))

        io_group = tk.LabelFrame(bbox, text="I/O", padx=padx, pady=pady)
        io_group.pack(fill=tk.BOTH, expand=1)
        tk.Label(io_group, text="Input port:").grid(row=0, column=0)
        self.in_port = tk.Entry(io_group)
        self.in_port.grid(row=0, column=1)
        self.in_port.insert(0, str(DEF_DPIN))
        tk.Label(io_group, text="Output port:").grid(row=0, column=2)
        self.out_port = tk.Entry(io_group)
        self.out_port.grid(row=0, column=3)
        self.out_port.insert(0, str(DEF_DPOUT))

        extras_group = tk.LabelFrame(bbox, text="Extras", padx=padx, pady=pady)
        extras_group.pack(fill=tk.BOTH, expand=1)
        save_group = tk.Frame(extras_group)
        save_group.pack(fill=tk.BOTH, expand=1)
        self.savefile = tk.IntVar()
        tk.Checkbutton(save_group, text="Save output?", variable=self.savefile).grid(row=0, column=0)
        tk.Label(save_group, text="     Location:").grid(row=0, column=1)
        self.savefilename = tk.Entry(save_group, width=30)
        self.savefilename.grid(row=0, column=2, padx=5)
        self.savefilename.insert(0, os.path.join(os.path.expanduser('~'), DEF_FILENAME))
        tk.Button(save_group, text="Browse", command=self.saveasdialog).grid(row=0, column=3)
        self.show_time = tk.IntVar()
        tk.Checkbutton(extras_group, text="Show simulation time", variable=self.show_time).pack(side=tk.LEFT)

        out_group = tk.LabelFrame(bbox, text="Output", padx=padx, pady=pady)
        out_group.pack(fill=tk.BOTH, expand=1)
        self.out_text = tk.Text(out_group, width=50, height=5)
        self.out_text.bind("<Key>", lambda e: "break")
        self.out_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        run_group = tk.Frame(bbox, padx=padx, pady=pady)
        run_group.pack(fill=tk.BOTH, expand=1)
        self.run_sim = tk.Button(run_group, text="Run Simulation", command=self.run_simulation)
        self.run_sim.pack(side=tk.RIGHT)

        self.after(0, self.deiconify)
        
    def on_closing(self):
        self.withdraw()
        self.quit()
        self.destroy()

    def saveasdialog(self):
        filename = filedialog.asksaveasfilename(initialdir = os.path.expanduser('~'),title = "Select file",filetypes = (("MATLAB Files","*.mat"),("All files","*.*")))
        if filename:
            self.savefilename.insert(0, filename)

    def run_simulation(self):
        sims = int(self.num_sims.get())
        s_width = float(self.sigma_width.get())
        s_thick = float(self.sigma_thickness.get())
        s_length = float(self.sigma_length.get())
        m_width = float(self.mean_width.get())
        m_thick = float(self.mean_thickness.get())
        m_length = float(self.mean_length.get())
        iport = int(self.in_port.get())
        oport = int(self.out_port.get())
        save = self.savefile.get() == 1
        location = self.savefilename
        timeit = self.show_time.get() == 1

        run_monte_carlo_sim(num_sims=sims, mu_width=m_width, sigma_width=s_width, mu_thickness=m_thick, sigma_thickness=s_thick, mu_length=m_length,
            sigma_length=s_length, dpin=iport, dpout=oport, saveData=save, filename=location, dispTime=timeit, printer=self.print_to_output)

    def print_to_output(self, message):
        self.out_text.insert(tk.END, message + "\n")

def run_monte_carlo_sim(num_sims=DEF_NUM_SIMS, mu_width=DEF_MU_WIDTH, sigma_width=DEF_SIGMA_WIDTH, mu_thickness=DEF_MU_THICKNESS,
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

def main():
    run_monte_carlo_sim()

def monte_carlo_simulation():
    app = MonteCarloGUI()
    app.mainloop()
  
if __name__ == "__main__":
    app = MonteCarloGUI()
    app.mainloop()
