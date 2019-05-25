import pya
import sys
import os
import h5py
from SiEPIC.ann import waveguideNN as wn

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "models/wg_ann/NN_SiO2_neff.h5")
model = wn.loadWaveguideNN(path)
#print(model)