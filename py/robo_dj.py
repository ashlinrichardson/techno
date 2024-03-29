bpm = 127 # should have an arg for this! NEED OPTION TO SET BPM!!
# ALSO NEED OPTION TO SET NUMBER OF BEATS WIDE: WINDOW 1, WINDOW 2, SLIDE WINDOW..
# NEED AN OPTION FOR WAV START...

import os
import sys
from work_queue import work_queue

args = sys.argv
sep = os.path.sep
exists = os.path.exists
reqd, to_install = ['sox', 'ffmpeg', 'soundstretch'], [] # , 'py38', 'py38-pip'], []

def err(msg):
    print("Error: " + msg)
    sys.exit(1)

if len(args) < 2:
    err("robo_dj.py [input directory containing mp3 or m4a files]")
args[1] = args[1].rstrip().rstrip(sep)

if not os.path.exists(args[1]):
    err("please check input folder")

def run(cmd):
    print("> " + cmd)
    a = os.system(cmd)
    if a != 0:
        err("command failed: " + cmd)

def is_installed(cmd):
    where = os.popen("which " + cmd).read().strip()
    return os.path.exists(where)

for req in reqd: # check each req'd terminal command
    if not is_installed(req):
        # req = "soundtouch" if req == "soundstretch" else req
        to_install.append(req) # soundstretch command lives in soundtouch

def install(cmd): # install a terminal command
    my_os = os.popen("uname").read().strip()

    if my_os == 'Linux':
        cmd = 'sudo apt install ' + cmd
    elif my_os == 'Darwin':
        if is_installed("brew"):
            cmd = 'sudo brew install ' + cmd
        elif is_installed("port"):
            cmd = 'sudo port install ' + cmd
        else:
            err("neither brew nor port package-manager found: pls install one and try again!")
    else:
        err("os: " + my_os + " not supported yet, sorry!")
    print("attempting to install " + cmd + " with command:")
    print("\t" + cmd)
    run(cmd)

for req in to_install: install(req)  # install required command

# step one: convert to wav
files = None
q = work_queue()
wav_dir = args[1] + "_wav" + sep
if not exists(wav_dir):
    os.mkdir(wav_dir)
    files = [x.strip() for x in os.popen("ls -1 " + args[1]).readlines()]
else:
    files = [x.strip() for x in os.popen("ls -1 " + wav_dir).readlines()]

for f in files: # convert each file to wav, if not already done!
    wav_f = '"' + wav_dir + f[:-3] + 'wav"'
    if not exists(wav_f.strip('"')):
        q.add('ffmpeg -i "' + args[1] + sep + f + '" ' + wav_f)
q.run()

# step two: adjust rate
wav_dir2 = args[1] + "_wav2" + sep
if not exists(wav_dir2): os.mkdir(wav_dir2)
files = [x.strip() for x in os.popen("ls -1 " + wav_dir).readlines()]
for f in files:
    wav_f = '"' + wav_dir + f[:-3] + 'wav"'
    wav_f2 = '"' + wav_dir2 + f[:-3] + 'wav"'
    print(wav_f, wav_f2)
    if not exists(wav_f2.strip('"')):
        q.add("sox " + wav_f + ' -r 44100 -b 16 ' + wav_f2)
q.run()

# step three: detect bpm
files, bpmf, ci = [x.strip() for x in os.popen("ls -1 " + wav_dir2).readlines()], [], 0
for f in files:
    wav_f2 = '"' + wav_dir2 + f[:-3] + 'wav"'
    bpm_f = str(ci) + ".bpm"
    bpmf.append(bpm_f)
    if not exists(bpm_f):
        cmd = ("soundstretch " + wav_f2 + " -bpm > " + bpm_f + " 2>&1")
        q.add(cmd)
    ci += 1
q.run()

# parse bpm
avg_bpm, n_bpm = 0., 0.
for f in bpmf:
    lines = [x.strip() for x in open(f).readlines()]
    for line in lines:
        w = line.split()
        print(w)
        try:
            if w[0] == 'Detected' and w[1] == 'BPM' and w[2] == 'rate':
                avg_bpm += float(w[3])
                n_bpm += 1
        except:
            pass

avg_bpm /= n_bpm
open("avg.bpm", "wb").write((str(avg_bpm)).encode())
bpm = avg_bpm

# step four: adjust bpm
wav_dir3, ci = args[1] + "_wav3" + sep, 0
if not exists(wav_dir3): os.mkdir(wav_dir3)
files = [x.strip() for x in os.popen("ls -1 " + wav_dir2).readlines()]
for f in files:
    wav_f2, bpm_f = '"' + wav_dir2 + f[:-3] + 'wav"', str(ci) + ".bpm2"
    wav_f3 = '"' + wav_dir3 + f[:-3] + 'wav"'
    print(wav_f2, wav_f3)
    if not exists(wav_f3.strip('"')):
        q.add("soundstretch " + wav_f2 + " " + wav_f3 + " -bpm=" + str(bpm) + " > " + bpm_f + " 2>&1")
    ci += 1
q.run()

# find pairwise correlations between tracks to be stitched
run("python3 py/correlate.py " + wav_dir3)

# determine ordering from pairwise correlations, then stitch using moving window technique
run("python3 py/stitch.py " + wav_dir3)

# last step: use sox to concatenate a list of wave files
files = open("file_list.txt").readlines()

s = "sox " # sox default action to concatenate
for f in files:
  s += f.strip() + " "
s += " out.wav" # output file

a = os.system(s)
print("convert out.wav to mp3.wav..")
a = os.system("ffmpeg -i out.wav out.mp3") # convert output to mp3 for upload / share
print("done")
