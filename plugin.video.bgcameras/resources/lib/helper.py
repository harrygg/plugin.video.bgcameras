# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcgui, xbmcaddon, time, xbmcplugin, base64, gzip
from datetime import datetime, timedelta
reload(sys)  
sys.setdefaultencoding('utf8')
	
clist = []
categories = []
id = 'plugin.video.bgcameras'
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
	
addon = xbmcaddon.Addon(id=id)
res = None
aName = 'assets.json'
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
afp = os.path.join(profile, aName)
#Settings

showDisabledCams =  True if addon.getSetting('show_disabled') == "true" else False
debug =  True if addon.getSetting('debug') == "true" else False
useRemoteAssets = True# if addon.getSetting('listType') == "0" else False
remoteAssetsUrl =  'http://rawgit.com/harrygg/plugin.video.bgcameras/master/plugin.video.bgcameras/resources/lib/assets.json.gz'
#remoteAssetsUrl =  'http://swvm1022.bgr.hp.com/assets.json.gz'
localAssetsPath =  addon.getSetting('file')
usePrivateList = True if addon.getSetting('usePrivateList') == "1" else False
privateListFile = addon.getSetting('privateListFile')
privateCat = {"name":"Частни камери", "id":"0", "count": 0}

def Log(msg, level = xbmc.LOGERROR):
  xbmc.log(" | " + id + " | " + str(msg), level)  
  
def Request(url, ref = ''):
  global response
  try:
    req = urllib2.Request(url)
    if ref == '': 
      ref = url
    xbmc.log("%s | Request() | url=%s, ref=%s" % (id, url, ref))
    req.add_header('Referer', ref)
    req.add_header('User-Agent', ua)
    res = urllib2.urlopen(req)
    r = res.read()
    res.close()
    return r
  except Exception, er:
    if debug: Log(res)
    else: Log(str(er))

def Extract(path):
	try:
		gz = gzip.GzipFile(path, 'rb')
		s = gz.read()
		gz.close()
		out = file(afp, 'wb')
		out.write(s)
		out.close()
		#return True
	except:
		raise

def CreateDir(path):
	try: os.makedirs(os.path.dirname(path))
	except OSError as exc: # Guard against race condition
		if exc.errno != errno.EEXIST:
			raise
				
def DownloadAssets():
  try:
    path = afp if not remoteAssetsUrl.endswith('.gz') else afp + ".gz"
    f = urllib2.urlopen(remoteAssetsUrl)
    if not os.path.exists(os.path.dirname(path)):
      CreateDir(path)
    with open(path, "wb") as code:
      code.write(f.read())
    Extract(path)
  except Exception, er:
    Log(er)
    raise
   
def LoadAssets(file = ""):
  global clist, categories
  if file.endswith('.gz'):
    df = gzip.open(file,'rb')
  else:
    df = open(file)
  content = json.load(df)
  df.close()
  categories = content['categories']
  clist = content['assets']
  if usePrivateList and privateListFile != '': #if there are private cameras, append them to the list
    AppendPrivateCameras()
    categories.append(privateCat)
  
 
def AppendPrivateCameras():
  if usePrivateList and privateListFile != '':
    with open(privateListFile) as f:
      try:
        c = f.read()
        names = re.compile('#EXTINF:\-1,\s*(.*)').findall(c)
        urls = re.compile('(http.*|rtsp.*|rtmp.*)').findall(c)
        if len(names) == len(urls):
          for i in range(0, len(names)):
            cam = {}
            cam["c"] = '0'
            cam["n"] = base64.b64encode(names[i])
            cam["u"] = base64.b64encode(urls[i])
            global clist
            clist.append(cam)
          privateCat['count'] = i + 1 #update private camera count
      except: pass

def AddCategories():
  for i in range (0, len(categories)):
    name = "%s (%s)" % (categories[i]['name'], categories[i]['count'])
    li = xbmcgui.ListItem(name, iconImage = "", thumbnailImage = "")
    li.setInfo( type = "Video", infoLabels = { "Title" : categories[i]['name'] } )
    li.setProperty("IsPlayable", 'False')
    u = "%s?c=%s&mode=View" % (sys.argv[0], categories[i]['id'])
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, True)

def Enabled(cam):
  return "d" not in cam.keys() or cam["d"] == 0

def AddItems(c):
  for i in range (0, len(clist)):
    cam = clist[i]
    if cam['c'] == c:
      if showDisabledCams or Enabled(cam):
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

def GetStream(i):
  cam = clist[i]
  stream = ''  
  if 'u' in cam.keys() and cam['u'] != "":
    return base64.b64decode(cam['u'])
  elif 'pl' in cam.keys() and 'pa' in cam.keys():
    pl = base64.b64decode(cam['pl'])
    pa = base64.b64decode(cam['pa'])
    res = Request(pl, pa) 
    m = re.compile('video.+src[=\s"\']+(.+?)[\s"\']+', re.DOTALL).findall(res)
    if m > 0:
      stream = m[0]
  Log(" | GetStream() will return %s" % stream)
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

#load assets
try:
  if not useRemoteAssets and localAssetsPath != '': #if we use local assets load it every time
    afp = localAssetsPath
  else: #using a remote file. Check if the file is too old
    if os.path.exists(afp):
      treshold = datetime.now() - timedelta(hours=6)
      fileModified = datetime.fromtimestamp(os.path.getmtime(afp))
      if fileModified < treshold: #file is more than a day old
        DownloadAssets()
    else: #file does not exist, perhaps first run
      DownloadAssets()
  LoadAssets(afp)
except Exception, er:
  Log(er)
  LoadAssets(os.path.join(os.path.dirname(os.path.realpath(__file__)), aName))
  xbmc.executebuiltin('Notification(%s,%s,10000,%s)' % ('BG Cameras', 'Неуспешно сваляне на най-новият списък с камери',''))