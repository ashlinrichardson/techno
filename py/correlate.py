# given a collection of wave files, produce a matrix of special correlations
import os
import sys
import math
import pickle

if os.path.exists("grid.pickle"):
    sys.exit(0)

def run(cmd):
    print(cmd)
    a = os.system(cmd)
    if a != 0:
        print("Error: command failed: " + cmd)
        sys.exit(1)

try: import matplotlib.pyplot as plt
except: run("python3 -m pip install matplotlib")

try: import scipy
except: run("python3 -m pip install scipy")

try: import numpy
except: run("python3 -m pip install numpy")

import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np

args, sep = sys.argv, os.path.sep
wavs = [x.strip() for x in os.popen("ls -1 " + args[1] + sep + "*.wav").readlines()]
grid = np.zeros((len(wavs), len(wavs))) # output grid of correlations

X = []
for i in range(len(wavs)):
	f = wavs[i]
	print("read", f) # first wav file to read
	samplerate, data = wavfile.read(f)
	L1 = data.shape[0]

	for j in range(len(wavs)): # could parallelize over this coord
		g = wavs[j]
		print("read", g) # second wav file to read
		samplerate2, data2 = wavfile.read(g)
		L2 = data2.shape[0]
		L = min(L1, L2) # minimum length
		L = math.floor(L/2)

		# cut out that size from both
		A = data[-L:, :] # cut from right side of A
		B = data2[:L, :] # cut from left side of B
		
		if(A.shape != B.shape):
			print(L, L1, L2)
			print(data.shape, data2.shape)
			print(A.shape, B.shape)
			sys.exit(1)

		grid[i, j] = np.sum(np.abs(np.dot(np.transpose(A), B)))
		X.append(grid[i,j])

with open("grid.pickle", "wb") as f:
	pickle.dump(grid, f)

X.sort() # sort the list in increasing order
print(X[0]) # print out first and last for debug
print(X[-1])
