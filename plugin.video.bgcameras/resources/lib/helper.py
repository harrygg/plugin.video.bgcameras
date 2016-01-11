# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcgui, xbmcaddon, time, xbmcplugin, base64
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

	

cameras = []
clist = []
categories = []
id = 'plugin.video.bgcameras'
mUrl = 'http://kamerite.novatv.bg/'
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
cookie = None
addon = xbmcaddon.Addon(id=id)
aName = 'assets.json'
a = []
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
afp = os.path.join(profile, aName)
#Settings
DisableAssetsCache = True
showDisabled =  True if addon.getSetting('show_disabled') == "true" else False
useRemoteAssets = True if addon.getSetting('listType') == "0" else False
remoteAssetsUrl =  addon.getSetting('url')
localAssetsPath =  addon.getSetting('file')

class Camera:
	name = None
	url = None
	icon = None
	pa = None
	pl = None
	
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

def Log(msg, level = xbmc.LOGERROR):
	xbmc.log(" | " + id + " | " + str(msg), level)	
	
def GetNewAssetsList():
	try:
		if useRemoteAssets == True:
			res = Request(remoteAssetsUrl)
			global clist, categories
			clist = json.loads(res)['assets']
			categories = json.loads(res)['categories']
			with open(afp, "w") as f:
				f.write(res)
		else:
			LoadAssets(localAssetsPath)
			
	except Exception, er:
		Log(er)

def LoadAssets(file = ""):
	df = open(file) 
	global clist, categories
	content = json.load(df)
	categories = content['categories']
	clist = content['assets']
	df.close()
	
#load assets
try:
	
	if DisableAssetsCache == True or useRemoteAssets == False:
		GetNewAssetsList()
	else:
		#check if assets file exist in profile folder
		if os.path.exists(afp):
			#check if the file is older than a day
			day_ago = datetime.now() - timedelta(days=1)
			file_modified = datetime.fromtimestamp(os.path.getmtime(afp))
			if file_modified < day_ago: #file is more than a day old
				GetNewAssetsList()
			else: #file is new
				LoadAssets(afp)
		else: #file does not exist, perhaps first run
			GetNewAssetsList()
except Exception, er:
	Log(er)
	#xbmcgui.Dialog().ok('Free BG TVs - channels.json error', 'Проблем със зареждането на списъка с камери.')
	xbmc.executebuiltin('Notification(%s,%s,10000,%s)'%('BG Cameras', 'Неуспешно сваляне на последната версия на списъка с камери',''))
	LoadAssets(os.path.join(os.path.dirname(os.path.realpath(__file__)), aName))
		         

def AddCategories():
	for i in range (0, len(categories)):
		li = xbmcgui.ListItem(categories[i]['name'], iconImage = "", thumbnailImage = "")
		li.setInfo( type = "Video", infoLabels = { "Title" : categories[i]['name'] } )
		li.setProperty("IsPlayable", 'False')
		u = "%s?c=%s&mode=View" % (sys.argv[0], categories[i]['id'])
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, True)

def AddItems(c):
		for i in range (0, len(clist)):
			cam = clist[i]
			if cam['c'] == c:
				if "d" not in cam.keys() or cam["d"] == 0:
					AddItem(i)

def AddItem(i):
	name = base64.b64decode(clist[i]['n'])
	li = xbmcgui.ListItem(name, iconImage = "", thumbnailImage = "")
	li.setInfo( type = "Video", infoLabels = { "Title" : name } )
	li.setProperty("IsPlayable", 'True')
	u = "%s?i=%s&mode=Play" % (sys.argv[0], i) #urllib.quote_plus(camera.url.encode('utf-8')))
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, False)

def Play(i):
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = GetStream(i)))

def CreateCameraObject(a):
	if "d" not in a.keys() or a["d"] == 0:
		c = Camera()
		c.name = base64.b64decode(a["n"])
		c.url = base64.b64decode(a["u"])
		c.icon = ''
		cameras.append(c)

#Get the cameras ones a day


def GetStream(i):
	cam = clist[i]
	stream = ''	
	
	if 'u' in cam.keys() and cam['u'] != "":
		return base64.b64decode(cam['u'])
	elif 'pl' in cam.keys() and 'pa' in cam.keys():
		pl = base64.b64decode(cam['pl'])
		pa = base64.b64decode(cam['pa'])
		res = Request(pl, pa)
		try: 
			bs = BeautifulSoup(res)
			src = bs.video["src"]
		except: 
			m = re.compile('video.+src[=\s"\']+(.+?)[\s"\']+.*</video', re.DOTALL).findall(res)
			stream = m[0]
	xbmc.log("%s | GetStream() returned %s" % (id, stream))
	#http://ios.cdn.bg:2019/fls/ipcam2.stream/playlist.m3u8?at=9fef1a19f37ecb5b24517690c047c9ed
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
