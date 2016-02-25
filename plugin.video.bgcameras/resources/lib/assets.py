# -*- coding: utf-8 -*-
import sys
from xbmcswift2 import Plugin

reload(sys)
sys.setdefaultencoding('utf8')

categories = ['София', 'Пловдив', 'Други']

items = [{
  'label': cat,
  'path': plugin.url_for('show_category'),
  'is_playable': False
} for cat in categories]

