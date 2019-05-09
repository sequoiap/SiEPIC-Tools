import pya
import sys
import os
import numpy as np
import copy
from SiEPIC.ann import getSparams as gs
from SiEPIC.ann import cascade_netlist as cn
from scipy.io import savemat
import time

start = time.time()
dispTime = False

num_sims = 10

mu_width = 0.5
sigma_width = 0.005
random_width = np.random.normal(mu_width, sigma_width, num_sims)

mu_thickness = 0.22
sigma_thickness = 0.002
random_thickness = np.random.normal(mu_thickness, sigma_thickness, num_sims)

gs.generateNetlist()
s, frequency = gs.getSparams(random_width[0], random_thickness[0])
results_shape = np.append(np.asarray([num_sims]), s.shape)
results = np.zeros([dim for dim in results_shape], dtype='complex128')

for sim in range(num_sims):
    results[sim, :, :, :] = gs.getSparams(random_width[sim], random_thickness[sim])[0]

p = gs.getPorts(random_width[0], random_thickness[0])
p = [int(i) for i in p]
rp = copy.deepcopy(p)
rp.sort(reverse=True)
concatinate_order = [p.index(i) for i in rp]
temp_res = copy.deepcopy(results)
re_res = np.zeros(results_shape, dtype=complex)

i=0
for idx in concatinate_order:
    re_res[:,:,i,:]  = temp_res[:,:,idx,:]
    i += 1
temp_res = copy.deepcopy(re_res)
i=0
for idx in concatinate_order:
    re_res[:,:,:,i] = temp_res[:,:,:,idx]
    i+= 1    
results = copy.deepcopy(re_res)

stop = time.time()

if dispTime == True:
    print(stop-start)

savemat('Desktop/mc_results.mat', {'freq':frequency, 'results':results})