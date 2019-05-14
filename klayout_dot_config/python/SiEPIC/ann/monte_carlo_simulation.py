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


# optional timer
# change dispTime to True to print elapsed time upon termination
start = time.time()
dispTime = True

# number of MC simulations to run
num_sims = 1000

# mean and standard deviation for width
mu_width = 0.5
sigma_width = 0.005
# random distribution for width
random_width = np.random.normal(mu_width, sigma_width, num_sims)

# mean and standard deviation for thickness
mu_thickness = 0.22
sigma_thickness = 0.002
# random distribution for thickness
random_thickness = np.random.normal(mu_thickness, sigma_thickness, num_sims)

# mean and standard deviation for length
mu_length = 0
sigma_length = 0.01
# random distribution for length change
random_deltaLength = np.random.normal(mu_length, sigma_length, num_sims)

# run simulation with mean width and thickness
mean_s, frequency = gs.getSparams(mu_width, mu_thickness, 0)
results_shape = np.append(np.asarray([num_sims]), mean_s.shape)
results = np.zeros([dim for dim in results_shape], dtype='complex128')

# run simulations with varied width and thickness
for sim in range(num_sims):
    results[sim, :, :, :] = gs.getSparams(random_width[sim], random_thickness[sim], random_deltaLength[sim])[0]
    if (sim % 10) == 0:
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
if dispTime == True:
    print('Total simulation time: ')
    print(stop-start)

# save MC simulation results to matlab file
savemat('Desktop/mc_results.mat', {'freq':frequency, 'results':results, 'mean':mean_s})

# plot histogram of varied responses with ideal response overlayed
# for port 2->1 
res21 = results[:, :, 1, 0]
res21 = 10*np.log10(abs(res21)**2)
res21 = np.reshape(res21, (res21.shape[0]*res21.shape[1]))
freq = frequency
for sim in range(1, num_sims):
    freq = np.append(freq, frequency)


mean_s21 = mean_s[:, 1, 0]
mean_s21 = 10*np.log10(abs(mean_s21)**2)

peak_locs = np.array([])
peaks = np.array([])
for sim in range(num_sims):
    data = results[sim, :, 1, 0]
    data = -10*np.log10(abs(data)**2)
    peak_locs = np.append(peak_locs, [frequency[int(i)] for i in find_peaks(data, prominence=3)[0]])
    peaks = np.append(peaks, [data[int(i)] for i in find_peaks(data, prominence=3)[0]])

plt.figure(1)
plt.hist2d(freq, res21, bins=1000, cmap=plt.cm.Blues_r)
plt.colorbar()
#plt.plot(frequency,  mean_s21, 'k', linewidth=0.5)
#plt.plot(peak_locs, -peaks, 'r*')
title = 'Monte Carlo Simulation (' + str(num_sims) + ' Runs)'
plt.title(title)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.draw()
plt.show()
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
#plt.savefig('Desktop/MC_results.png')

'''
plt.figure(2)
plt.hist(peak_locs, 10)
title = 'Variance of Peaks'
plt.title(title)
plt.xlabel('Frequency (Hz)')
plt.draw()
plt.show()
'''

