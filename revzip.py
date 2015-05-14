import os
from os.path import join, getsize

def extract_assets(src,dst):
	os.system("xcopy \"%s\" \"%s\" /s /e"%(src,dst))

	for root, dirs, files in os.walk(src):
		for name in files:
			full = join(root,name)
			if full.endswith(".zip"):
				os.system("7z x \"%s\" -aoa -o%s%s"%(full,dst,root[len(src):]))

	for root, dirs, files in os.walk(dst):
		for name in files:
			full = join(root,name)
			if full.endswith(".zip"):
				os.remove(full)

if __name__ == '__main__':
	extract_assets(
		r'E:\Game\Disney Interactive\Disney Infinity PC\asset-cache\base\image\assets',
		r'I:\DisneyInfinityAssets')