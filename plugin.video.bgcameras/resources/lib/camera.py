
def Camera:

	def __init__(self, attr):
		self.id = attr[0]
		self.category = attr[1]
		self.inactive = True if attr[2] == 1 else False
		self.name = attr[3]
		self.stream = attr[4]
		self.streamrtsp = attr[5]
		self.playerurl = attr[6]
		self.pageurl = attr[7]
		self.logo = attr[8]