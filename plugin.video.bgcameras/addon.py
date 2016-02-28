# -*- coding: utf-8 -*-
import sys
from xbmcswift2 import Plugin, xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.assets import *

reload(sys)
sys.setdefaultencoding('utf8')

plugin = Plugin()
addon_id = 'plugin.video.bgcameras'
addon = xbmcaddon.Addon(id = addon_id)
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
afp = os.path.join(profile, 'assets.sqlite')

category = 0

#plugin entry screen Categories
@plugin.route('/')
def index():
	cats = GetCategories(afp)
	items = [{
		'label': cat.name, 
		'path': plugin.url_for('show_category', category=cat.id), 
		'is_playable': False
	}	for cat in cats]
	return items

#Display videos for the provided category
@plugin.route('/<category>/')
def show_category(category):
  #items = get_items(category) 
  #return plugin.finish(items)
  pass


if __name__ == '__main__':
    plugin.run()
