# use sox to concatenate a list of wave files
import os

files = open("file_list.txt").readlines()

s = "sox " # sox default action to concatenate
for f in files:
	s += f.strip() + " "
s += " ../out.wav" # output file

a = os.system(s)
