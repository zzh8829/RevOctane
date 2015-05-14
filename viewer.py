import OpenGL
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
import time
import random
import colorsys

import os
import sys
import revoctane
import bstream
import diutil

#sys.stdout = open("viewer.log","w")

SCREEN_SIZE = 1280,600
SCREEN_FLAG = OPENGL|DOUBLEBUF|HWSURFACE
os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
pygame.display.set_mode(SCREEN_SIZE,SCREEN_FLAG)
font = pygame.font.SysFont("Arial",18)

def gltexture(surface=None,file=None):
	if file:
		surface = pygame.image.load(file)

	surface = pygame.transform.flip(surface,False,True)
	width = surface.get_width()
	height = surface.get_height()
	data = pygame.image.tostring(surface,"RGBA",1)
	texture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D,texture)

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_REPEAT)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_REPEAT)

	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,GL_RGBA,GL_UNSIGNED_BYTE, data)
	glGenerateMipmap(GL_TEXTURE_2D);
	return texture

def glinit():
	glClearColor(0,0,0,1)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_ALPHA_TEST)
	glAlphaFunc(GL_GREATER, 0.5)
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

def glresize(width, height):
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60.0, float(width)/height, .1, 1000.)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

path = "Research/"
#path = "I:/DisneyInfinityAssets"

di = diutil.DIUtil(path)

#char = "wr_vanellope"
char = "fro_elsa"
#char = "blobshadow"
#char = '_proxyavatar'
#char = 'inc_scourge_pod'
#char = 'booster'
#char = 'lr_traintrack_switch'
#char = 'zurg_ship'
#char = 'inc_floating_disc'
#char = 'inc_phonebooth'
#char = 'jetpack'
#char = 'ts_fartplant'
#char = 'biped'

#tex = "5260e82d41b31ee1"
#tex = "6146379f6f179819"

#tex = gltexture(file=di.char_tex(char,tex))
tex = 0

os.chdir(di.char_dir(char))
obj = di.char_oct(char)

ibuf = bstream.BStream(file=obj.IndexBufferPool[0].FileName)
vbuf = bstream.BStream(file=obj.VertexBufferPool[0].FileName)

ivals = []
while ibuf.get_position()!=ibuf.size():
	ivals.append(ibuf.read('uint16'))

flists = []
ilists = []
vlists = []

maxb = 0

for index, node in obj.SceneTreeNodePool.items():
	if 'Primitives' in node:
		for index, primitive in node.Primitives.items():
			idata = primitive.Idata
			vdata = primitive.Vdata

			vformat = primitive.vformatCRC

			fg = []
			fg.append(vformat)
	
			ipos = idata[1]
			ilen = idata[3]

			ilist = []
			for i in range(ilen//3):
				indices = []
				for j in range(3):
					indices.append(ivals[ipos+i*3+j])
				ilist.append(indices)
			ilists.append(ilist)	

			vlen = vdata[1]
			vbeg = vdata[3]
			vwidth = vdata[4]
			vbeg2 = vdata[6]
			vwidth2 = vdata[7]

			if vformat == 0x6133d27b:
				print("Mesh Bone")
				'''
				1
				pos: f32,f32,f32 
				uv: f16,f16
				bonei: ui8,ui8,ui8,ui8  bonei contains 0-39, but there are 64 influences in oct file, idk :(
				bonew: ui8,ui8,ui8,ui8  since sum of bonew = 255, w[i]/255 should be weight 
				2
				normal: f16,f16,f16,f16
				binormal: f16,f16,f16,f16
				'''

				vbuf.set_position(vbeg)
				vlist = []
				for i in range(vlen):
					v = []
					for j in range(3):
						v.append(vbuf.read('float'))
					for j in range(2):
						v.append(vbuf.read('float16'))
					for j in range(4):
						v.append(vbuf.read('uint8'))
					for j in range(4):
						v.append(vbuf.read('uint8'))

					vlist.append(v)
					maxb = max(maxb,max(v[5:9]))

				vbuf.set_position(vbeg2)
				for i in range(vlen):
					for j in range(8):
						vlist[i].append(vbuf.read('float16'))
					
			elif vformat == 0xea1acc4c:
				print("Mesh Plain")
				'''	
				1
				pos: f32,f32,f32
				uv: f16,f16
				2
				normal: f16,f16,f16,f16
				binormal: f16,f16,f16,f16
				'''

				vbuf.set_position(vbeg)
				vlist = []
				for i in range(vlen):
					v = []
					for j in range(3):
						v.append(vbuf.read('float'))
					for j in range(2):
						v.append(vbuf.read('float16'))
					vlist.append(v)

				vbuf.set_position(vbeg2)
				for i in range(vlen):
					for j in range(8):
						vlist[i].append(vbuf.read('float16'))
			elif vformat == 0x01890ff9:
				print("Mesh Plain2")
				'''	
				1
				pos: f32,f32,f32
				uv: f16,f16
				2
				normal: f16,f16,f16,f16
				binormal: f16,f16,f16,f16
				unknown: i32
				'''

				vbuf.set_position(vbeg)
				vlist = []
				for i in range(vlen):
					v = []
					for j in range(3):
						v.append(vbuf.read('float'))
					for j in range(2):
						v.append(vbuf.read('float16'))
					vlist.append(v)

				vbuf.set_position(vbeg2)
				for i in range(vlen):
					for j in range(8):
						vlist[i].append(vbuf.read('float16'))
					vlist[i].append(vbuf.read('int32'))
			else:
				print("Mesh Unknown")

			vlists.append(vlist)

			flists.append(fg)


print("Loaded")

cs = []
csn = (maxb+2)*255
for i in range(csn):
	hsv = i/csn, 0.5, 0.5
	cs.append(colorsys.hsv_to_rgb(*hsv))

dlists = []

for f,i,v in zip(flists,ilists,vlists):
	d = glGenLists(1)
	glNewList(d, GL_COMPILE)

	glColor(1,1,1,1)
	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D,tex)
	glBegin(GL_TRIANGLES)
	

	if f[0] == 0x6133d27b:
		for j in range(len(i)):
			i1,i2,i3 = i[j]
			#glColor(cs[v[i1][5]*255 + v[i1][9]])
			glTexCoord(*v[i1][3:5])
			glVertex(v[i1][:3])
			#glColor(cs[v[i2][5]*255 + v[i2][9]])
			glTexCoord(*v[i2][3:5])
			glVertex(v[i2][:3])
			#glColor(cs[v[i3][5]*255 + v[i2][9]])
			glTexCoord(*v[i3][3:5])
			glVertex(v[i3][:3])
	elif f[0] == 0xea1acc4c or f[0] == 0x01890ff9:
		for j in range(len(i)):
			i1,i2,i3 = i[j]
			glVertex(v[i1][:3])
			glVertex(v[i2][:3])
			glVertex(v[i3][:3])

	glEnd()

	glEndList()

	dlists.append(d)

print("DisplayList")

ang = 0

enabled = [True]*20

def render():
	global ang

	glPushMatrix()

	glTranslate(0,-2,-5)
	glRotate(ang,0,1,0)

	ang += 1

	for i in range(len(dlists)):
		if enabled[i]:
			glCallList(dlists[i])

	glPopMatrix()

glinit()
glresize(*SCREEN_SIZE)

running = True
lasttime = time.time()

while running:
	delta = time.time()-lasttime
	lasttime += delta

	for e in pygame.event.get():
		if e.type == QUIT:
			running =  False
		elif e.type == KEYDOWN:
			if e.key == K_ESCAPE:
				running = False
			if ord('0') <= e.key <= ord('9'):
				v = e.key - ord('0')
				if v == 0:
					enabled = [True]*20
				else:
					enabled[v-1] = not enabled[v-1]

	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

	render()

	pygame.display.flip()

pygame.quit()
