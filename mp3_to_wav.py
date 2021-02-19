# convert mp3 or m4a files to wav
import os
import sys

def run(c):
	print(c)
	a = os.system(c)

mp3 = [x.strip() for x in os.popen("ls -1 *.m*").readlines()]

for f in mp3:
	run('ffmpeg -i "' + f + '" "' + f[:-3] + 'wav"')
