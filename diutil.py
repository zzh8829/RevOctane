import os
import sys
import code

import revoctane
import bstream

class DIUtil:
	
	def __init__(self, asset_path):
		self.asset_path = asset_path

	def char_oct(self, name):
		return revoctane.Octane(bstream.BStream(
			file=os.path.join(self.char_dir(name),"%s.oct"%name)))
	def char_ct(self, name):
		return revoctane.Octane(bstream.BStream(
			file=os.path.join(self.char_dir(name),"%s.bct"%name)))
	def char_bent(self, name):
		return revoctane.Octane(bstream.BStream(
			file=os.path.join(self.char_dir(name),"%s.bent"%name)))
	def char_anm(self, name, anm, name2=None):
		if not name2:
			name2 = name
		return revoctane.Octane(bstream.BStream(
			file=os.path.join(
				self.char_dir(name),"characters",name2,"motions","%s.oct"%anm)))
	def char_dir(self, name):
		return os.path.join(self.asset_path,"characters",name)

	def char_tex(self, name, tex):
		return os.path.join(self.char_dir(name),textures,"%s.tbody.png"%tex)

	def dump_all(self, output_path, input_path=''):
		asset_dir = os.path.join(self.asset_path, input_path)
		for root, dirs, files in os.walk(asset_dir):
			for name in files:
				full = os.path.join(root,name)
				stream = bstream.BStream(file=full)
				if stream.size() > 4 and stream.read(4) == b'\x29\x76\x01\x45':
					os.makedirs(
						output_path + root[len(asset_dir):], exist_ok=True)
					stream.set_position(0)
					obj = revoctane.Octane(stream)
					if obj._state == 'fail':
						sys.stderr.write(full+"\n")
					obj.dump(
						open(output_path + full[len(asset_dir):] + ".txt","w"))

	def walk(self, path):
		for root, dirs, files in os.walk(path):
			for name in files:
				yield os.path.join(root,name)

	def console(self, *args):
		var = {}
		for i in args:
			var.update(i)
		con = code.InteractiveConsole(var)
		con.interact("DI Console")

	