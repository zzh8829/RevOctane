import pprint
import collections
import sys
import code
import uuid
import copy
import itertools

import bstream
import diutil

class Octane(collections.OrderedDict):

	MAGIC = 1157723689,1066192077

	def __init__(self, stream=None, *args, **kwargs):
		super(Octane, self).__init__(*args, **kwargs)
		self._state = 'init'
		self._strings = []
		self._lines = []
		self._idx = 0
		if stream:
			self.read(stream)

	def __getitem__(self, key):
		return super(Octane, self).__getitem__(str(key))

	def __setitem__(self, key, value):
		return super(Octane, self).__setitem__(str(key), value)

	def __getattr__(self, item):
		if item in self:
			return self.__getitem__(item)
		else:
			return self.__getattribute__(item)

	def __setattr__(self, key, value):
		if key in self:
			return self.__setitem__(key,value)
		else:
			return super(Octane, self).__setattr__(key, value)

	def __str__(self):
		return self.to_string(0)

	def copy(self): 
		obj = Octane()
		for key,val in self.items():
			if isinstance(val, Octane):
				obj[key] = val.copy()
			else:
				obj[key] = copy.deepcopy(val)
		return obj

	def to_string(self, indent=0):
		strs = ""
		for k,v in self.items():
			if isinstance(v,Octane):
				strs += indent*'\t' + k + ' = ' + '\n' + v.to_string(indent+1)
			else:
				strs += indent*'\t' + k + ' = ' + str(v) + '\n'
		return strs

	def read(self, stream):
		
		magic = stream.read("uint32"),stream.read("uint32")
		if magic != Octane.MAGIC:
			print("WARNING: WRONG MAGIC")

		padding = stream.read("uint32")
		string_size = stream.read("uint32")
		data_size = stream.read("uint32") 
		padding = stream.read(40)

		header_size = stream.tell()

		self._strings = []
		while stream.tell() != header_size + string_size:
			self._strings.append(stream.read_cstring())
		
		self._lines = []
		Line = collections.namedtuple('Line',['indent','format','name','data'])

		while stream.tell() != header_size + string_size + data_size:
			flag = stream.read("uint16_t")
			name = self._strings[stream.read("uint16_t")]

			indent,format = divmod(flag,0x400)

			if format == 0x01: 
				data = None
			elif format == 0x05: 
				data = self._strings[stream.read("uint16_t")]
			elif format == 0x0A:
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(self._strings[stream.read("uint16_t")])
			elif format == 0x0B:
				data = self._strings[stream.read("uint16_t")]
			elif format == 0x0F:
				data = [self._strings[stream.read("uint16_t")],self._strings[stream.read("uint16_t")]]
			elif format == 0x12:
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(stream.read("float"))
			elif format == 0x13:
				data = stream.read("float")
			elif format == 0x16:
				head = self._strings[stream.read("uint16_t")]
				count = stream.read("uint8_t")
				data = [head]
				for i in range(count):
					data.append(stream.read("float"))
			elif format == 0x1A:
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(stream.read("int8_t"))
			elif format == 0x1B:
				data = stream.read("int8_t")
			elif format == 0x1F:
				data = [self._strings[stream.read("uint16_t")],self._strings[stream.read("uint8_t")]]
			elif format == 0x23:
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(stream.read("uint8_t"))
			elif format == 0x4A:
				count = stream.read("uint16_t")
				data = []
				for i in range(count):
					data.append(self._strings[stream.read("uint16_t")])
		#	elif format == 0x52:
		# 		unknown
			elif format == 0x5A:
				count = stream.read("uint16_t")
				data = []
				for i in range(count):
					data.append(stream.read("uint8_t"))
			elif format == 0x56:
				head = self._strings[stream.read("uint16_t")]
				count = stream.read("uint16_t")
				data = [head]
				for i in range(count):
					data.append(stream.read("float"))
			elif format == 0x63: # binary data
				count = stream.read("uint16_t")
				data = stream.read(count)
				#data = []
				#for i in range(count):
				#	data.append(stream.read("uint8_t"))
			elif format == 0xA3:
				count = stream.read("uint12_t")
				data = []
				for i in range(count):
					data.append(stream.read("uint8_t"))
			elif format == 0x11A:
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(stream.read("uint16_t"))
			elif format == 0x11B:
				data = stream.read("uint16_t")
			elif format == 0x15A:
				count = stream.read("uint16_t")
				data = []
				for i in range(count):
					data.append(stream.read("uint16_t"))
			elif format == 0x21A:
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(stream.read_int12())
			elif format == 0x21B:
				data = stream.read_int12()
			elif format == 0x31A: # Not Sure
				count = stream.read("uint8_t")
				data = []
				for i in range(count):
					data.append(stream.read('uint32_t'))
			elif format == 0x31B:
				data = stream.read("uint32_t")
			else:
				data = "Error! format: %x indent: %x offset: %x"%(format,indent,stream.get_position())
				self._lines.append(Line(indent,format,name,data))
				self._state = 'fail'
				sys.stderr.write("Error! format: %x indent: %x offset: %x\n"%(format,indent,stream.get_position()))
				break
				#raise Exception("Unknown Format")

			self._lines.append(Line(indent,format,name,data))

		self.construct()

	def construct(self):
		self._idx = 1 # ignore first line
		self.update(self.construct_dict(0))

	def construct_dict(self, indent):
		obj = Octane()
		while self._idx != len(self._lines):
			line = self._lines[self._idx]
			self._idx += 1
			if line.indent <= indent:
				self._idx -= 1
				break
			if line.indent > indent:
				if line.format == 0x01:
					obj[line.name] = self.construct_tree(line.indent)
				else:
					obj[line.name] = line.data
		return obj

	def construct_tree(self, indent):
		obj = Octane()
		node = 0
		while self._idx != len(self._lines):
			line = self._lines[self._idx]
			self._idx += 1
			if line.indent <= indent:
				self._idx -= 1
				break
			elif line.indent > indent:
				if line.format == 0x01:
					obj[node] = self.construct_dict(line.indent)
					node += 1
				elif line.format in [0x16,0x56]:
					obj[line.data[0]] = line.data[1:]
				elif line.format == 0x05:
					obj[line.data] = self.construct_dict(line.indent)
				else:
					obj[line.name] = line.data
		return obj

	def dump(self, out=sys.stdout):
		for line in self._lines[1:]: # ignore first line
			data = line.data
			if data == None:
				data = ""
			elif isinstance(data,str):
				data = '"%s"'%data
			else: 
				data = str(data)
			out.write((line.indent-1)*"\t" + line.name + "[%04x]"%line.format + " = " + data + "\n")

def basis(subnetwork, idx):
	return subnetwork.BasisPool[idx]

def data_node(subnetwork, idx):
	hs = subnetwork.HeaderStrings
	hsi = subnetwork.HeaderStringIndices
	dn = subnetwork.DataNodePool[idx].copy()
	dn.Header = hs[hsi[dn.Header]]
	if "BasisRef" in dn:
		dn['Basis'] = basis(subnetwork,dn.BasisRef)
	return dn

def basis_conversion(obj):
	for subnetwork in obj.SubNetworkPool.values():
		for bc in subnetwork.BasisConversionPool.values():
			bcc = bc.copy()
			bcc['FromBasis'] = basis(subnetwork, bcc.FromBasisRef)
			bcc['ToBasis'] = basis(subnetwork, bcc.ToBasisRef)
			bcc['DataNode'] = data_node(subnetwork, bcc.DataNodeRef)
			pprint.pprint(bcc)

	
def connection_map(obj):
	for subnetwork in obj.SubNetworkPool.values():
		for idx in subnetwork.ConnectionMapUsedDataNodes:
			pprint.pprint(data_node(subnetwork,idx))

def component_family(obj):
	for subnetwork in obj.SubNetworkPool.values():
		dnp = subnetwork.DataNodePool

		cn = subnetwork.ComponentNames
		#print(subnetwork)
		for cf in subnetwork.ComponentFamilyPool.values():
			patriarch = data_node(subnetwork, cf.PatriarchDataNodeRef)
			data = []
			for idx,ref in zip(cf.ComponentNameIndices,cf.ComponentDataNodeRefs):
				data.append((cn[idx],data_node(subnetwork,ref)))
			print("patriarch")
			pprint.pprint(patriarch)
			print("component")
			pprint.pprint(data)
			print()

def association(obj):
	for ass in obj.AssociationPool.values():
		assc = ass.copy()
		#if scene

def clip_data(obj):
	return bstream.BStream(bytes=bytes(obj.SubNetworkPool[0].DataNodePool[0].ClipDataBlock))

def clip(obj):
	fstream = clip_data(obj)
	f16stream = clip_data(obj)
	i8stream = clip_data(obj)
	i16stream = clip_data(obj)
	i32stream = clip_data(obj)

	while fstream.tell() != fstream.size():
		print("%13e, %13f %13f, %4d %4d %4d %4d, %6d %6d, %10d"%(
			fstream.read("float"),
			f16stream.read("float16"),f16stream.read("float16"),
			i8stream.read("int8_t"),i8stream.read("int8_t"),i8stream.read("int8_t"),i8stream.read("int8_t"),
			i16stream.read("int16_t"),i16stream.read("int16_t"),
			i32stream.read("int32_t")))

	print(fstream.size())

def clip2(obj):
	stream = clip_data(obj)

	ext = []

	def e(s):
		ext.append(stream.read(s))

	ext.append(stream.read("uint32")) # pad
	ext.append(stream.read("float")) # time
	ext.append(stream.read("uint16")) # un1
	ext.append(stream.read("uint16")) # un2
	offset = stream.read("uint32") # float offset
	ext.append(offset) 

	op = stream.tell()
	stream.seek(offset,0)
	data = []
	while stream.tell() != stream.size():
		data.append(stream.read("float"))
	stream.seek(op,0)
	ext.append(data)
	ext.append(len(data))

	e("uint32")
	e("uint32")


	'''
	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")

	e("uint16")
	e("uint16")
	'''
	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("uint8")
	e("uint8")

	e("float")

	e("float")
	e("float")
	e("float")
	e("float")

	e("float16") # 0
	e("float16")

	e("float16")
	e("float16")

	e("float16")

	e("float16") # ERR 
	e("float16")

	e("float16")
	#ext.append((stream.read("float16")))

	while stream.tell() < offset:
		ext.append((stream.tell(),stream.read("uint8")))
	
	ext.append(stream.size())

	return ext 

def pp(l):
	a = ""
	for i in l:
		a += "%-6d"%i
	return a

def slice_anm(obj):
	stream = clip_data(obj)
	b = stream.read_all()
	
	deli = bytes([0,0,0,0,0x66,0x66,0x86,0x40])
	beg = False
	pos = 0
	l = []
	for i in range(0,len(b)-8):
		if b[i:i+8] == deli:
			if beg:
				l.append(b[pos:i])
				pos = i
			else:
				beg = True
	l.append(b[pos:])
	return l

def clip3(obj):
	stream = clip_data(obj)

	zero = stream.read("int32")
	time = stream.read("float")

	one = stream.read("int16")
	count = stream.read("int16")
	float_offset = stream.read("int32")
	uk_offset = stream.read("int32")

	offsets = []
	for i in range(count):
		offsets.append(stream.read("int32"))

	print(time,one,count,float_offset,uk_offset,offsets)

	offsets.append(float_offset)

	data = []
	u1 = stream.read("int16")
	print(u1)
	cnt = stream.read("int16")
	for i in range(cnt):
		data.append(stream.read("int16"))
	print(cnt,data)

	data = []
	while stream.tell() < offsets[0]:
		data.append(stream.read("uint16"))
	print(len(data))
	print(pp(data))

	for i in range(count):
		data = []
		while stream.tell() != offsets[i+1]:
			data.append(stream.read("uint8"))
		print(len(data),data)

	data = []
	while stream.tell() != stream.size():
		data.append(stream.read("float"))
	print(len(data),data)


if __name__ == '__main__':
	elsa = Octane(bstream.BStream(file="fro_elsa.oct"))
	elsa.dump(open("fro_elsa.ipad.oct.txt","w"))
	#luigi = Octane(bstream.BStream(file="Research/luigi/effects/a_1_dmmxtcdum_skin.tfx",endianness="big"))
	#luigi.dump(open("asdf.txt","w"))
	di = diutil.DIUtil("I:/DisneyInfinityAssets")
	di = diutil.DIUtil("Research")
	obj = di.char_oct("ts_fartplant")
	obj.dump(open("dump.txt","w"))

	sys.stdout = open("output.txt","w")

	basis_conversion(obj)
	print("###")
	connection_map(obj)
	print("###")
	component_family(obj)
	print("###")

	snp = obj.SubNetworkPool
	sn = snp[0]
	dnp = sn.DataNodePool
 
	goo = di.char_ct("googrowshrink")
	open("dump2.txt","w").write(goo.to_string())
	#idle = di.char_anm("ts_fartplant","fplant_idle")
	g2n = di.char_anm("ts_fartplant","goo_grown2normal","googrowshrink")
	n2g = di.char_anm("ts_fartplant","goo_normal2grown","googrowshrink")
	s2n = di.char_anm("ts_fartplant","goo_shrunk2normal","googrowshrink")
	n2s = di.char_anm("ts_fartplant","goo_normal2shrunk","googrowshrink")

	eia = di.char_anm("fro_elsa","elsa_bm_idle_active")

	clip3(eia)
	clip3(g2n)

	print("###")

	cks =  slice_anm(eia)
	print(len(cks))
	for i in cks:
		print(len(i))

	fps = [g2n,n2g,s2n,n2s, eia]
	fprs = [clip2(i) for i in fps]

	for e in zip(*fprs):
		pprint.pprint(e)
		print()

	#eia = di.char_anm("fro_elsa","elsa_bm_idle_active")
	#eac = di.char_anm("fro_elsa","elsa_atk_combo1")
	#efh = di.char_anm("fro_elsa","elsa_face_happy1")
	#eva = di.char_anm("fro_elsa","elsa_vsm_aa")

	di.console(globals(),locals())


