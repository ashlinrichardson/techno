import os
import sys
import math
import copy
import pickle
import numpy as np
from parfor import parfor
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
args, sep = sys.argv, os.path.sep
file_list = open("file_list.txt", "wb") # record files to merge
wavs = [x.strip() for x in os.popen("ls -1 " + args[1]).readlines()]
a = os.system("rm tmp*.wav") # clean up intermediary files

bpm = float(open("avg.bpm").read().strip())

window_secs = 3.78  # window size for comparison: need to scale window size for bpm
drag_width = 3.78 * 4  #  3.78 * 4 # how far to drag the window!

mpb = 1. / bpm # minutes per beat
spb = 60. / bpm # seconds per beat

window_secs = 8 * spb

drag_width = window_secs * 4 # make this factor adjustable

d = pickle.load(open("grid.pickle", "rb")) # grid of correlations from dot.py
plt.imshow(d)
plt.savefig("grid.png") # plot the correlations

t = []
N = d.shape[0]
for i in range(d.shape[0]):
    for j in range(d.shape[1]):
        if i != j:
            t.append([-d[i,j], i, j])
t.sort(reverse=True)  # which way? try the other

lookup = {}
for ti in t:
    d, i, j = ti
    if not i in lookup: lookup[i] = []
    lookup[i].append(ti)

for i in lookup:
    lookup[i].sort(reverse=True)
    print(i, lookup[i])
    rng = []
    for ti in lookup[i]:
        d, m, n = ti
        rng.append(n)
    print("  ", i, rng)
    if len(rng) != len(set(rng)):
        print("error:"); sys.exit(1)

here = t[0][1] # index of start track
visited = [here]
# print("here", here)
# print("visited", visited)

for i in range(N - 1): # find T[n+1] # print(i, "here", here, "wavs", wavs[here])
    while lookup[here][0][2] in visited:
        lookup[here] = lookup[here][1:]
    my_next = lookup[here][0][2]
    visited.append(my_next)
    here = my_next

print(visited)
print(len(set(visited)))
print(len(visited))
for v in visited: print('"' + wavs[v] + '"')

print("len(visited)", len(visited))
if len(visited) != len(wavs):
    print("err"); sys.exit(1)



start = 0
data, data2, samplerate, samplerate2 = None, None, None, None
for i in range(len(visited) - 1):
    j = visited[i]
    f = args[1] + sep + wavs[j] # filename of song to transition from
    print("read[" + f + "]"); samplerate, data = wavfile.read(f)
    L1 = data.shape[0]

    j = visited[i + 1]
    f = args[1] + sep + wavs[j] # filename of song to transition to!
    print("read", f); samplerate2, data2 = wavfile.read(f)
    L2 = data2.shape[0]

    print(L1, L2)
    data_R = data2[0 : math.floor(samplerate * window_secs), :] # take the first samplerate*windowsec of R, slide it back over L
    corr = np.zeros(math.floor(drag_width * samplerate))

    dx_max = 0 # shift for local alignment of clip
    step = 11 # step size for windowed search

    '''
    for dx in range(1, math.floor(drag_width * samplerate), step): # should parallelize this part!
        if dx % 100 == 0:
            print(dx, "/", math.floor(drag_width * samplerate))
        data_L = data[-(math.floor(samplerate * window_secs) + dx): - dx, :]
        m = np.sum((np.dot(np.transpose(np.abs(data_L)), np.abs(data_R)))) # our correlation measure
        corr[dx] = m
        if m > dx_max:
            dx_max = m  # find the max of the correlation measure

    '''
    rng = range(1, math.floor(drag_width * samplerate), step)

    def calc_m(dx):
        #if dx % 100 == 0:
        #    print(dx, "/", math.floor(drag_width * samplerate))
        data_L = data[-(math.floor(samplerate * window_secs) + dx): - dx, :]
        return np.sum((np.dot(np.transpose(np.abs(data_L)), np.abs(data_R))))

    m_s = parfor(calc_m, rng) # calculate the correlation function in parallel

    for dxi in range(len(rng)):
        dx = rng[dxi]
        m = m_s[dxi]
        corr[dx] = m
        if m > dx_max:
            dx_max = m  # find max of the correlation measure

    data_L = data[-( math.floor(samplerate * window_secs) + dx_max): - dx_max, :]

    if False:
        plt.plot(data_L[:, 0])
        plt.plot(data_R[:, 0])

    t = np.linspace(0., 1., data_L.shape[0])
    u = 1. - t
    print("data_L.shape", data_L.shape)
    print("data_R.shape", data_R.shape)

    dataL = copy.deepcopy(data_L)
    dataR = copy.deepcopy(data_R)

    for k in range(2): # perform the interpolation
        dataL[:, k] = np.multiply(u, data_L[:,k])
        dataR[:, k] = np.multiply(t, data_R[:,k])

    out = dataL + dataR # write("tmp.wav", samplerate, out.astype(np.int16))

    # 1. write transition-from track (until transition)..
    to_xsition = data[start : -(math.floor(samplerate * window_secs) + dx_max), :]
    file_list.write(("tmp_" + str(i) + ".wav\n").encode())
    write("tmp_" + str(i) + ".wav", samplerate, to_xsition.astype(np.int16)) # write first clip up to transition!

    file_list.write(("tmp_xsit_" + str(i) + ".wav\n").encode())
    write("tmp_xsit_" + str(i) + ".wav", samplerate, out.astype(np.int16)) # write transition
    # 3. set start index for next write
    start = math.floor(samplerate * window_secs) #  + dx_max) # where to pick up from on next clip!

    if False:
        plt.show()

    #plt.plot(corr)
    #plt.show()
    print(dx_max / samplerate)
    print("attempt..")

file_list.write(("tmp_last.wav").encode())
file_list.close()

data2 = data2[start: , :] # cut the redundant section off the last clip too!
write("tmp_last.wav", samplerate, data2.astype(np.int16)) # write remainder of last track
