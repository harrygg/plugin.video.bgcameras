# -*- coding: utf-8 -*-
import sys
from xbmcswift2 import Plugin
#from resources.lib.assets import *

reload(sys)
sys.setdefaultencoding('utf8')

plugin = Plugin()

categories = ['София', 'Пловдив', 'Други']
category = 0

#items = [{
#  'label': cat,
#  'path': plugin.url_for('show_category'),
#  'is_playable': False
#} for cat in categories]


#plugin entry screen Categories
@plugin.route('/')
def index():
  items = [{'label': categories[i], 'path': plugin.url_for('show_category', category=i), 'is_playable': False} for i in range (0, len(categories))]
  return items

#Display videos for the provided category
@plugin.route('/<category>/')
def show_category(category):
  #items = get_items(category) 
  #return plugin.finish(items)
  pass

#categories = ['София', 'Пловдив', 'Други']




if __name__ == '__main__':
    plugin.run()
