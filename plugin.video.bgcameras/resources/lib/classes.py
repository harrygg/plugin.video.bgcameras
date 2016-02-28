# -*- coding: utf-8 -*-
import sys, os, re, sqlite3, requests, gzip, urllib2

reload(sys)
sys.setdefaultencoding('utf8')

### Class Categories
class Category:
	def __init__(self, attr):
		self.id = attr[0]
		self.name = attr[1]
		self.count = attr[2]

### Class Camera
class Camera:
	def __init__(self, attr):
		l = len(attr)
		self.id = attr[0]
		self.inactive = attr[2]
		self.name = attr[3]
		self.stream = attr[4]
		if l > 5:
			self.stream_rtsp = attr[5]
			if l > 6:
				self.player_url = attr[6]
				if l > 7:
					self.page_url = attr[7]
					if l > 8:
						self.logo = attr[8]

	def _resolve(self):
		from urlparse import urlparse
		stream = ''
		headers = {
			'User-Agent' : 'stagefright',
			'Referer' : self.page_url }

		r = requests.get(self.player_url, headers=headers)
		parser = urlparse(self.page_url)
		if parser.hostname == 'ipcamlive.com':
			m = re.compile('address[=\s\'"]+(.*?)[\'"\s]+', re.DOTALL).findall(r.text)
			if len(m) > 0:
				stream = m[0]
			m = re.compile('streamid[=\s\'"]+(.*?)[\'"\s]+', re.DOTALL).findall(r.text)
			if len(m) > 0:
				stream = '%s/streams/%s/stream.m3u8' % (stream, m[0])
		else: #regular video stream
			m = re.compile('video.+src[=\s"\']+(.+?)[\s"\']+', re.DOTALL).findall(r.text)
			if len(m) > 0:
				stream = m[0]
		return stream

	def get_stream(self):
		if self.stream != None:
			return self.stream
		elif self.stream_rtsp != None:
			return self.stream_rtsp
		elif self.player_url != None:
			return self._resolve()
		else: 
			return ''

	def get_icon(self):
		try:
			import time
			ts = int(time.time())
			if '?' in self.logo:
				if self.logo.endswith('='):
					return "%s%s" % (self.logo, ts)
				else:
					return "%s&amp;ts=%s" % (self.logo, ts)
			else:
				return "%s?ts=%s" % (self.logo, ts)
		except:
			return ''

### Class PrivateCameras
class PrivateCameras:
	def __init__(self, file):
		self.id = 0
		self.name = 'Частни камери'
		self.cameras = []
		self.count = 0
		with open(file) as f:
			try:
				c = f.read()
				names = re.compile('#EXTINF:\-1,\s*(.*)').findall(c)
				urls = re.compile('(http.*|rtsp.*|rtmp.*)').findall(c)
				
				if len(names) == len(urls):
					for i in range(0, len(names)):
						cam = Camera(['p'+str(i), 0, 0, names[i], urls[i]])
						self.cameras.append(cam)
						self.count = self.count + 1
			except Exception, er:
				helper.plugin.log.error(str(er))

	def get_camera(self, id = 'p'):
		for c in self.cameras:
			if c.id == id:
				return Camera([c.id, 0, 0, c.name, c.stream])

### Class Helper
class Helper:

	def __init__(self, plugin):
		self.plugin = plugin
		self.local_db = os.path.join(plugin.storage_path, 'assets.sqlite')
		self.use_private_list = True if plugin.addon.getSetting('usePrivateList') == "1" else False
		if self.use_private_list:
			self.private_list_file = plugin.addon.getSetting('privateListFile')
		
	def get_categories(self):
		categories = []
		conn = sqlite3.connect(self.local_db)
		cursor = conn.execute('''
			SELECT cat.id, cat.name, COUNT(*) 
			FROM cameras AS cam 
			JOIN categories AS cat 
			WHERE cat.id == cam.category_id 
			GROUP BY cam.category_id'''
		)
	
		for row in cursor:
			cat = Category(row)
			categories.append(cat)

		if self.use_private_list and self.private_list_file != '':
			pc = PrivateCameras(self.private_list_file)
			categories.append(Category([pc.id, pc.name, pc.count]))
		return categories
	
	def get_cameras(self, category_id = 1):
		cameras = []
		if int(category_id) != 0:
			conn = sqlite3.connect(self.local_db)
			cursor = conn.execute("SELECT * FROM cameras WHERE category_id == ?", category_id)
			for row in cursor:
				cam = Camera(row)
				cameras.append(cam)
		else:
			pc = PrivateCameras(self.private_list_file)
			cameras = pc.cameras
		return cameras

	def get_stream(self, camera_id = 1):
		stream = ''
		if 'p' not in camera_id:
			conn = sqlite3.connect(self.local_db)
			cursor = conn.execute("SELECT * FROM cameras WHERE id == ?", camera_id)
			cam = Camera(cursor.fetchone())
			stream = cam.get_stream()
		else:
			pc = PrivateCameras(self.private_list_file)
			cam = pc.get_camera(camera_id)
			stream = cam.stream
		return stream

	def download_assets(self):
		try:
			remote_db = 'http://rawgit.com/harrygg/plugin.video.bgcameras/master/plugin.video.bgcameras/resources/storage/assets.sqlite.gz'
			plugin.log.info('Downloading assets from url: %s' % remote_db)
			save_to_file = self.local_db if not remote_db.endswith('.gz') else self.local_db + ".gz"
			f = urllib2.urlopen(remote_db)
			with open(save_to_file, "wb") as code:
				code.write(f.read())
			self.extract(save_to_file)
		except Exception, er:
			self.plugin.log.error(er)
			raise

	def extract(self, path):
		try:
			gz = gzip.GzipFile(path, 'rb')
			s = gz.read()
			gz.close()
			out = file(self.local_db, 'wb')
			out.write(s)
			out.close()
		except:
			raise

