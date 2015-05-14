import bstream
import os

def rev_mtb(stream):
	magic = stream.read(4) #BNDL
	header = stream.read(12)

	print(magic)
	print(header)

	name = stream.read_cstring()
	pad = stream.read(2)

	filename = stream.read(8)

	print(filename)

if __name__ == '__main__':
	os.chdir("Research")
	rev_mtb(bstream.BStream(file="cube.mtb"))
