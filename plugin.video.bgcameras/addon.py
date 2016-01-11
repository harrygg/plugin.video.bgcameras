# -*- coding: utf-8 -*-
import re, sys, os.path, urllib, urllib2
from resources.lib.helper import *		

reload(sys)  
sys.setdefaultencoding('utf8')
params = GetParams()

i = 0
try: i = int(params["i"])
except: pass

mode = None
try: mode = params["mode"]
except: pass
	
c = None
try: c = params["c"]
except: pass
	
if mode == None: 
	AddCategories()
elif mode == "View":
	AddItems(c)
else: 
	Play(i)

xbmcplugin.endOfDirectory(int(sys.argv[1]))