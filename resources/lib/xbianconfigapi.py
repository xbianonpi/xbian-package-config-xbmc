import os,time

#API mode
SET = 0
GET = 1

class API():
	def __init__(self,mode) :
		self.mode = mode
	
	def dispatch(self,funcname,data=None):
		service = getattr(self,funcname)
		return service(data)
	
	def subSetting(self,varname):
		var = getattr(self,varname)
		return var
	
	def resize(self,data):
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'resize',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			#must return have to resize (true/false)
			return "true"
		
		
	def overclock(self,data):
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'overclock',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "3"
		
	
	def hostname(self,data):
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'overclock',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "xbian"
		
	def rootpassword(self,data):
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'rootpassword',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "******"
		
	
	def xbianpassword(self,data):
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'xbianpassword',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "******"
		
	def wlan(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'wlan',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			return "true"
		
	
	def lan(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'lan',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
			pass
		elif self.mode == GET :
			#call xbian-config
			self.adress = '192.168.1.5'
			self.subnet = '255.255.255.0'
			self.gateway = '192.168.1.1'
			self.dns1 = '8.8.8.8'
			self.dns2 ='8.8.8.8'
			return "0"
			
		
	
	def rootlogin(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'rootlogin',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "false"
		
	
	def forcehdmi(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'forcehdmi',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "false"
		
	
	def ignorehdmi(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'ignorehdmi',str(data))
		if self.mode == SET :
			#simulate delay config
			#time.sleep(5)
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "false"
	
	def cecinit(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'cecinit',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "false"
	
	def cec(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'cec',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "false"
	
	def overscan(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'overscan',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "false"
	
	def vc1(self,data) :
		print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'rootlogin',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "0x"
	
	def mpeg2(self,data) :
		print 'API - self.mode : %d - Called to %s with params : %s'%(self.mode,'rootlogin',str(data))
		if self.mode == SET :
			#call xbian-config
			return True
		elif self.mode == GET :
			#call xbian-config
			return "0x"
	
APIset = API(SET)
APIget = API(GET)
	
	
