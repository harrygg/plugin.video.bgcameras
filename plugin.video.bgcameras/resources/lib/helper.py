# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcgui, xbmcaddon, time, xbmcplugin
from bs4 import BeautifulSoup

class Camera:
	name = None
	url = None
	icon = None

cameras = []
id = 'plugin.video.bgcameras'
mUrl = 'http://kamerite.novatv.bg/'
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
cookie = None

def Request(url, ref = ''):
	req = urllib2.Request(url)
	if ref == '': 
		ref = url
	xbmc.log("%s | Request() | url=%s, ref=%s" % (id, url, ref))
	req.add_header('Referer', ref)
	req.add_header('User-Agent', ua)
	res = urllib2.urlopen(req)
	global cookie
	cookie = res.info().getheader('Set-Cookie')
	if cookie != None:
		cookie = urllib.quote(cookie)
	r = res.read()
	res.close()
	return r
	
def AddItem(camera):
	li = xbmcgui.ListItem(camera.name, iconImage = camera.icon, thumbnailImage = camera.icon)
	li.setInfo( type = "Video", infoLabels = { "Title" : camera.name } )
	li.setProperty("IsPlayable", 'True')
	u = "%s?url=%s&mode=Play" % (sys.argv[0], urllib.quote_plus(camera.url.encode('utf-8')))
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, False)

def Play(url):
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = GetStream(url)))
	
#Get the cameras ones a day
try:
	res = Request(mUrl)
	bs = BeautifulSoup(res)
	boxes = bs.find_all("div", ["even", "odd"])
	for box in boxes:
		c = Camera()
		c.name = box.div.string + ", " + box.div.next_sibling.next_sibling.string
		c.url = box.a['href']
		#hack to bust caching of thumbnails
		c.icon = box.img['src'] + '?' + str(int(time.time()))
		cameras.append(c)
     
	#addon = xbmcaddon.Addon(id=id) 
	#profile = xbmc.translatePath( addon.getAddonInfo('profile'))
	#cameras = os.path.join(profile, 'cameras.json')

	#if os.path.exists(cameras):
		#f = open(cameras, 'w')
		#json.dump(clist, f)
		#f.write(clist)
		#f.close()

	#with open('data.json', 'r') as fp:
	#data = json.load(fp)

except Exception, er:
	xbmc.log(id + " | " + str(er))
	#xbmcgui.Dialog().ok(str(er))
	pass

def GetStream(url):
	stream = ''
	url = mUrl + url
	res = Request(url, url)
	bs = BeautifulSoup(res)
	src = bs.iframe["src"]	
	res = Request(src, url)
	m = re.compile('video.+src[="\']+(.+?)[\s"\']+').findall(res)
	if len(m) > 0:
		stream = m[0]
	#xbmc.log("%s | GetStream() returned %s" % (id, stream))
	return stream

def GetParams():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?','')
		if (params[len(params)-1] == '/'):
			params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]
	return param
