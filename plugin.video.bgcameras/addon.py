# -*- coding: utf-8 -*-
import re, sys, os.path, urllib, urllib2
from resources.lib.helper import *		

reload(sys)  
sys.setdefaultencoding('utf8')
params = GetParams()

url = None
try: url = params["url"]
except: pass

mode = None
try: mode = params["mode"]
except: pass
	
if mode == None: 
	for camera in cameras:
		AddItem(camera)
else: 
	Play(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))