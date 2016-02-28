# -*- coding: utf-8 -*-
import sys, os
from xbmcswift2 import Plugin, xbmc
from resources.lib.classes import *

reload(sys)
sys.setdefaultencoding('utf8')

plugin = Plugin('plugin.video.bgcameras')

#plugin entry screen camera categories
@plugin.route('/')
def index():
	cats = helper.get_categories()
	items = [{
		'label': "%s (%s)" % (cat.name, cat.count), 
		'path': plugin.url_for('show_category', category_id=cat.id), 
		'is_playable': False
	}	for cat in cats]
	return items

#Display cameras for the provided category
@plugin.route('/categories/<category_id>/')
def show_category(category_id):
	cams = helper.get_cameras(category_id)
	items = [{
		'label' : cam.name, 
		'path' : plugin.url_for('play_stream', camera_id=cam.id),
		'icon' : cam.get_icon(),
		'is_playable' : True
	}	for cam in cams]
	return items

#Play camera stream
@plugin.route('/cameras/<camera_id>/')
def play_stream(camera_id):
	stream = helper.get_stream(camera_id)
	plugin.log.info('Playing url: %s' % stream)
	plugin.set_resolved_url(stream)


helper = Helper(plugin)

#Check whether the assets file is old
try:
	from datetime import datetime, timedelta
	if os.path.exists(helper.local_db):
		treshold = datetime.now() - timedelta(hours=6)
		fileModified = datetime.fromtimestamp(os.path.getmtime(helper.local_db))
		if fileModified < treshold: #file is more than a day old
			helper.download_assets(helper.local_db)
	else: #file does not exist, perhaps first run
		helper.download_assets(helper.local_db)
except Exception, er:
	plugin.log.error(er)
	xbmc.executebuiltin('Notification(%s,%s,10000,%s)' % ('БГ Камерите', 'Неуспешно сваляне. Ще се използва лакален списък с камери',''))
	assets = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/storage/assets.sqlite.gz')
	helper.extract(assets)

#Run addon
if __name__ == '__main__':
    plugin.run()

