import pya
import sys
import os
import h5py
from SiEPIC.ann import waveguideNN as wn

#model = wn.loadWaveguideNN('/home/rumbonium/.klayout/python/SiEPIC/ann/NN_SiO2_neff.h5')
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "NN_SiO2_neff.h5")
model = wn.loadWaveguideNN(path)
print(model)