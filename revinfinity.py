import os
import io
import pprint
import sys
import struct

import bstream
import revoctane

def read_oct(stream):
	file_size = stream.size()

	magic = stream.read(12)
	header = stream.read(10)
	padding = stream.read(38)
	strings = []

	s = ""
	while s!="\x01":
		s = stream.read_cstring()
		strings.append(s)

	padding = stream.read(2)

	while stream.get_position() != file_size:
		flag = stream.read("uint16_t")
		name = strings[stream.read("uint16_t")]

		indent,format = divmod(flag,0x400)

		print("\t"*(indent-1) + name + "[%04x]"%format, end=" = ")

		# unknown sign all treat as unsigned !!!

		if format == 0x01: 
			print()
		elif format == 0x05: 
			data = strings[stream.read("uint16_t")]
			print("'%s'"%data)
		elif format == 0x0A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(strings[stream.read("uint16_t")])
			print(data)
		elif format == 0x0B:
			data = strings[stream.read("uint16_t")]
			print("'%s'"%data)
		elif format == 0x12:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("float"))
			print(data)
		elif format == 0x13:
			data = stream.read("float")
			print(data)
		elif format == 0x1A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("int8_t"))
			print(data)
		elif format == 0x1B:
			data = stream.read("int8_t")
			print(data)
		elif format == 0x23:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint8_t"))
			print(data)
		elif format == 0x4A:
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(strings[stream.read("uint16_t")])
			print(data)
		elif format == 0x5A:
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint8_t"))
			print(data)
		elif format == 0x63: # binary data
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint8_t"))
			print(data)
		elif format == 0x11A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint16_t"))
			print(data)
		elif format == 0x11B:
			data = stream.read("uint16_t")
			print(data)
		elif format == 0x15A:
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint16_t"))
			print(data)
		elif format == 0x21A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read_int12())
			print(data)	
		elif format == 0x21B:
			data = stream.read_int12()
			print(data)
		elif format == 0x31B:
			data = stream.read("uint32_t")
			print(data)
		else:
			print("unknown format: %x offset: %x"%(flag,stream.get_position()))
			sys.stderr.write("unknown format: %x offset: %x\n"%(flag,stream.get_position()))
			print(stream.read_all()[:100])
			break

def read_all(asset_dir,output_dir):
	#asset_dir = "I:/DisneyInfinityAssets"
	#output_dir = "I:/DisneyInfinityReversed"	
	for root, dirs, files in os.walk(asset_dir):
		for name in files:
			full = os.path.join(root,name)
			stream = bstream.BStream(file=full)
			if stream.size() > 4 and stream.read(4) == b'\x29\x76\x01\x45':
				os.makedirs(output_dir + root[len(asset_dir):], exist_ok=True)
				stream.set_position(0)
				obj = revoctane.Octane(stream)
				if obj._state == 'fail':
					sys.stderr.write(full+"\n")
				obj.dump(open(output_dir + full[len(asset_dir):] + ".txt","w"))

def get_char_dir(asset_dir, name):
	return "%s/characters/%s/"%(asset_dir,name)

def get_char_oct(asset_dir, name):
	return "%s/characters/%s/%s.oct"%(asset_dir,name,name)

def sort_char(asset_dir):
	l = []
	for name in os.listdir(asset_dir+"/characters"):
		try:
			fn = get_char_oct(asset_dir,name)
			if not os.path.exists(fn):
				continue
			sz = os.path.getsize(fn)
			l.append((name,sz))
		except Exception as e:
			print(e)

	l.sort(key=lambda t:(t[1],t[0]))
	pprint.pprint(l)
	
	for name,size in l:
		pp = []
		obj = revoctane.Octane(bstream.BStream(file=get_char_oct(asset_dir, name)))
		for index, node in obj.SceneTreeNodePool.items():
			if 'Primitives' in node:
				for index, primitive in node.Primitives.items():
					pp.append(hex(primitive.vformatCRC))
		if '0x6133d27b' in pp:
			print(name,pp)	
			input()
	return l

if __name__ == '__main__':
	#read_all("I:/DisneyInfinityAssets/characters","I:/DisneyInfinityAssets/characters")
	#sys.exit(0)
	#read_all("fro_elsa","fro_elsa")
	#sys.stdout = open("log.txt","w")
	#read_oct(BStream(file="Asset/fro_elsa/characters/biped/motions/biped_atk_genswing1.oct"))

	asset_dir = "I:/DisneyInfinityAssets"

	sort_char("I:/DisneyInfinityAssets")

	folder = os.getcwd() + "/"
	os.chdir("Research/")

	obj = revoctane.Octane(bstream.BStream(file=get_char_oct(asset_dir,"inc_scourge_pod")))
	obj.dump(open(folder + "log.txt","w"))

	path = get_char_dir(asset_dir,"inc_scourge_pod")
	os.chdir(path)

	vbuf = bstream.BStream(file=obj.VertexBufferPool[0].FileName)
	vbuf.set_position(547680)
	s = set()
	for i in range(748):
		vl = []
		for j in range(8):
			vl.append(vbuf.read('float16'))
		for j in range(1):
			vl.append(vbuf.read('int32'))
		print(vl)
		s.a



	strs = obj._strings 
	revoctane.console(globals(),locals())
	sys.stdout = open(folder + "output.txt","w")

	sys.exit(0)



