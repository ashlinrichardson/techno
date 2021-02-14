# produce a transformed set of wav files, all at rate 44100 Hz
import os

wavs = [x.strip() for x in os.popen("ls -1 *.wav").readlines()]

def run(c):
	print(c)
	a = os.system(c)

run("mkdir out")

for w in wavs:
	run("sox " + ' "' + w + '" -r 44100 -b 16 out/"' + w + '"') 
