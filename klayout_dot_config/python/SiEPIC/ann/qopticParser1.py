import pya
import io
import scipy.io as sio
import numpy as np
import cmath as cm

class Reader:
    '''
    class to extend the pya.Cell class with the functionality to read/parse 
    files containing s-parameter data for photonic components
    '''

    def readSparamData(filename, numports, isgc):
        '''
        Function that takes a file containing s-parameters, parses it, and 
        returns an array of frequency values and a 3D matrix of s-parameters
        Args:
            filename (str): name of file to be parsed
            numports (int): the number of ports the photonic component has
            isgc (boolean): flag indicating the component is a grating coupler
                            grating couplers are a special case
        Returns:
            S (3D list of complex-128): S-matrix for the component associated with the file
            F (list of float): Frequency array for the component associated with the file
        '''

        F = []
        S = []
        fid = open(filename, "r")
        
        if isgc is True:
            '''
            grating couplers have a different file format from the other component types
            so a special case is required to parse them
            '''

            #grating coupler compact models have 100 points for each s-matrix index
            arrlen = 100
            
            lines = fid.readlines()
            F = np.zeros(arrlen)
            S = np.zeros((arrlen,2,2), 'complex128')
            for i in range(0, arrlen):
                words = lines[i].split()
                F[i] = float(words[0])
                S[i,0,0] = cm.rect(float(words[1]), float(words[2]))
                S[i,0,1] = cm.rect(float(words[3]), float(words[4]))
                S[i,1,0] = cm.rect(float(words[5]), float(words[6]))
                S[i,1,1] = cm.rect(float(words[7]), float(words[8]))
            F = F[::-1]
            S = S[::-1,:,:]
        
        else:
            '''
            Common case
            Parsing a '.sparam' file
            '''

            line = fid.readline()
            line = fid.readline()
            numrows = int(tuple(line[1:-2].split(','))[0])
            S = np.zeros((numrows, numports, numports), dtype='complex128')
            r = m = n = 0
            for line in fid:
                if(line[0] == '('):
                    continue
                data = line.split()
                data = list(map(float, data))
                if(m == 0 and n == 0):
                    F.append(data[0])
                S[r,m,n] = data[1] * np.exp(1j*data[2])
                r += 1
                if(r == numrows):
                    r = 0
                    m += 1
                    if(m == numports):
                        m = 0
                        n += 1
                        if(n == numports):
                            break
        fid.close()
        return [S, F]
        
#extending the pya.Cell class
pya.Cell.Reader = Reader


def findPort(name, list):
    '''
    Search a list of cells for a port with a certain name
    Args:
        name (str): name of port to find
        list (list of cells)
    Returns:
        d (int): index of cell with matching port in its port list
        p (int): index of matching port within cell[d]
        returns [-1, -1] if name is not found in list
    '''

    for d in range(0, len(list)):
        for p in range(0, len(list[d].p)):
            if(list[d].p[p] == name):
                return [d, p]
    return [-1, -1]