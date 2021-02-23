# produce a transformed set of wave files, with consistent tempo
import os
import sys

n = 140 

wavs = [x.strip() for x in os.popen("ls -1 *.wav").readlines()]

def run(c):
	print(c)
	a = os.system(c)

run("mkdir out")

for w in wavs:
	run("soundstretch " + '"' + w + '" out/"' + w + '" -bpm=' + str(n))
