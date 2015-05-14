import io
import struct

little_endian_types = {
	'int8': 'b',
	'uint8': 'B',
	'int16': 'h',
	'uint16': 'H',
	'int32': 'i',
	'uint32': 'I',
	'int64': 'q',
	'uint64': 'Q',
	'float': 'f',
	'float32': 'f',
	'double': 'd',
	'char': 'c',
	'bool': '?',
	'pad': 'x',
	'void*': 'P',
}

big_endian_types = { k:">"+v for k,v in little_endian_types.items()}

special_types = {
	'int12': 'read_int12',
	'uint12': 'read_int12',
	'float16': 'read_float16',
}

class BStream:
	def __init__(self, **kwargs):
		if "file" in kwargs:
			self.stream = open(kwargs["file"], "rb")
		elif "stream" in kwargs:
			self.stream = kwargs["stream"]
		elif "bytes" in kwargs:
			self.stream = io.BytesIO(kwargs["bytes"])
		else:
			raise Exception("unknown stream source")

		self.endianness = kwargs.get("endianness","little")

		if self.endianness == "little":
			self.normal_types = little_endian_types
		elif self.endianness == "big":
			self.normal_types = big_endian_types

	def read(self, type_name='char'):
		if isinstance(type_name,int):
			return self.unpack('%ds'%type_name)[0]
		type_name = type_name.lower()
		if type_name.endswith('_t'):
			type_name = type_name[:-2]
		if type_name in special_types:
			return getattr(self, special_types[type_name])()
		if type_name in self.normal_types:
			return self.unpack(self.normal_types[type_name])[0]
		raise Exception("unknown type")

	def unpack(self, fmt):
		return struct.unpack(fmt, self.stream.read(struct.calcsize(fmt)))

	def read_cstring(self):
		string = ""
		while True:
			char = self.read('char')
			if ord(char) == 0:
				break
			string += char.decode("utf-8")
		return string

	def read_string(self):
		return self.unpack('%ds'%self.read('uint32_t'))[0].decode('utf-8')

	def read_all(self):
		return self.read(self.size() - self.get_position())

	def read_int12(self):
		return int.from_bytes(self.read(3),byteorder=self.endianness)

	def read_float16(self):
		data = self.read('uint16_t')

		s = int((data >> 15) & 0x00000001)    # sign
		e = int((data >> 10) & 0x0000001f)    # exponent
		f = int(data & 0x000003ff)            # fraction

		if e == 0:
			if f == 0:
				return int(s << 31)
			else:
				while not (f & 0x00000400):
					f = f << 1
					e -= 1
				e += 1
				f &= ~0x00000400
				#print(s,e,f)
		elif e == 31:
			if f == 0:
				return int((s << 31) | 0x7f800000)
			else:
				return int((s << 31) | 0x7f800000 | (f << 13))

		e = e + (127 -15)
		f = f << 13
		
		buf = struct.pack('I',int((s << 31) | (e << 23) | f))
		return struct.unpack('f',buf)[0]

	def tell(self):
		return self.stream.tell()

	def seek(self, pos, whence):
		return self.stream.seek(pos, whence)

	def get_position(self):
		return self.tell()

	def set_position(self, pos, whence=0):
		return self.seek(pos, whence)

	def size(self):
		pos = self.get_position()
		self.set_position(0,2)
		end = self.get_position()
		self.set_position(pos,0)
		return end

	def align(self, alignment=4):
		self.set_position((self.get_position() + alignment - 1) // alignment * alignment) 

