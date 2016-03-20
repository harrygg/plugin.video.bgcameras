<<<<<<< HEAD
﻿# -*- coding: utf-8 -*-
import sys
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
=======
# -*- coding: utf-8 -*-
import sys, os
from xbmcswift2 import Plugin
from resources.lib.classes import *

reload(sys)
sys.setdefaultencoding('utf8')
plugin = Plugin('plugin.video.bgcameras')

#plugin entry screen camera categories
@plugin.route('/')
def index():
	items = [{
		'label': "%s (%s)" % (cat.name, cat.count), 
		'path': plugin.url_for('show_category', category_id=cat.id), 
		'is_playable': False
	}	for cat in get_categories()]
	return items

#Display cameras for the provided category
@plugin.route('/categories/<category_id>/')
def show_category(category_id):
	items = []
	cams = get_cameras(category_id)
	for cam in cams:
		if cam.stream != '':
			path = cam.stream
		elif cam.stream_rtsp != '':
			path = cam.stream_rtsp
		else:
			path = plugin.url_for('play_stream', camera_id=cam.id)
		
		items.append({
			'label' : cam.name, 
			'path' : path,
			'icon' : cam.get_icon(),
			'is_playable' : True
		})

	return plugin.finish(items, view_mode=500)	

#Play camera stream
@plugin.route('/cameras/<camera_id>/')
def play_stream(camera_id):
	stream = get_stream(camera_id)
	plugin.log.info('Playing url: %s' % stream)
	plugin.set_resolved_url(stream)

@plugin.cached(240)
def get_categories():
	conn = sqlite3.connect(helper.local_db)
	cursor = conn.execute('''
		SELECT cat.id, cat.name, COUNT(*) 
		FROM cameras AS cam 
		JOIN categories AS cat 
		WHERE cat.id == cam.category_id 
		GROUP BY cam.category_id'''
	)
	categories = [Category(row) for row in cursor] 
	#Append private cameras if there are any
	pc = PrivateCameras(plugin)
	if pc.count > 0:
		categories.append(Category([pc.id, pc.name, pc.count]))
	return categories

@plugin.cached(240)
def get_cameras(category_id = 1):
	cameras = []
	if int(category_id) != 0: #Anything than 0 is private camera category
		conn = sqlite3.connect(helper.local_db)
		cursor = conn.execute('''SELECT * FROM cameras WHERE category_id == ?''', [category_id])
		for row in cursor:
			cam = Camera(row)
			cameras.append(cam)
	else:
		pc = PrivateCameras(plugin)
		cameras = pc.cameras
	return cameras

@plugin.cached(240)
def get_stream(camera_id = 1):
	stream = ''
	if 'p' not in camera_id: #Anything that starts with p is private camera id
		conn = sqlite3.connect(helper.local_db)
		cursor = conn.execute('''SELECT * FROM cameras WHERE id == ?''', (camera_id,))
		cam = Camera(cursor.fetchone())
		stream = cam.get_stream()
	else:
		pc = PrivateCameras(plugin)
		cam = pc.get_camera(camera_id)
		stream = cam.stream
	return stream

helper = Helper(plugin)
helper.check_assets()

#Run addon
if __name__ == '__main__':
	plugin.run()

 
>>>>>>> refs/remotes/origin/sqlite
