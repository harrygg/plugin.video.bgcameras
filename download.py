# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcgui, xbmcaddon, time, xbmcplugin, base64, gzip
afp = "C:\\Users\\genevh\\Documents\\GitHub\\plugin.video.bgcameras\\plugin.video.bgcameras\\resources\\lib\\assets.json"


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

try:
	remoteAssetsUrl = "https://kodibg.org/playlists/bgcameras/assets.json.gz"
	fileName = afp + ".gz"
	f = urllib2.urlopen(remoteAssetsUrl)
	with open(fileName, "wb") as code:
		code.write(f.read())
	Extract(fileName)
	
	df = open(afp)
	content = json.load(df)
	ver = "%s.%s.%s" %( content["version"]["major"], content["version"]["minor"], content["version"]["build"])

	print ""
	print "#########################"
	print ""
	print ""
	print "Build number: " + str(ver)
	print ""
	print ""
	print "#########################"
	
except Exception, er:
	print str(er)
	raise