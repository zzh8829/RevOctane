import os
from os.path import join, getsize

for root, dirs, files in os.walk('I:/DisneyInfinityAssets/characters'):
	for name in files:
		full = join(root,name)
		with open(full,"rb") as f:
			magic = f.read(4)
			if magic == b'\x1b\x4c\x75\x61':
				print(full)
				os.system("luadec %s > %s"%(full,full+".rev.lua"))