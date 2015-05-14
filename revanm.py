import os
import io
import pprint
import sys
import struct

import bstream
import revoctane

def getclip(obj):
	return obj.SubNetworkPool[0].DataNodePool[0].ClipDataBlock

def a2b(obj):
	pass

if __name__ == '__main__':
	obj = revoctane.Octane(bstream.BStream(file="I:/DisneyInfinityAssets/characters/ts_fartplant/ts_fartplant.oct"))
	idle = revoctane.Octane(bstream.BStream(file="I:/DisneyInfinityAssets/characters/ts_fartplant/"
		"characters/ts_fartplant/motions/fplant_idle.oct"))
	idle2 = revoctane.Octane(bstream.BStream(file="I:/DisneyInfinityAssets/characters/ts_fartplant/"
		"characters/ts_fartplant/motions/fplant_idle_stoodon.oct"))
	jump = revoctane.Octane(bstream.BStream(file="I:/DisneyInfinityAssets/characters/ts_fartplant/"
		"characters/ts_fartplant/motions/fplant_jump.oct"))
	revoctane.console(globals(),locals())