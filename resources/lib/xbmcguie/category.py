from tag import Tag
from xbmcContainer import GroupListControl,Content

import xbmc
import xbmcgui
from xbmcaddon import Addon

__addonID__      = "plugin.xbianconfig"


dialog = xbmcgui.Dialog()

#virtual Category Class
#bass Class for all categories

class Category():
    def __init__(self,queue) :
        self.setTitle(self.TITLE)
        self.queue = queue
        self.settings = []
        for setting in self.SETTINGS :
			self.settings.append(setting())
        self.category  = GroupListControl(Tag('onleft',9000),Tag('onright',9000),Tag('itemgap',-1),Tag('visible','Container(9000).HasFocus(%d)'%self.Menucategory.getId()),defaultSKin = False)
        for setting in self.settings :
			setting.addQueue(self.queue)
			self.category.addControl(setting.getControl())
        self.onInit()
    
    def onInit(self):
        pass
    
    def onClick(self,ctrlId):
		self.category.click(ctrlId)
		for setting in self.settings :
			setting.onClick(ctrlId)
        
    def setTitle(self,Title) :
        self.Title = Title
        self.Menucategory = Content(Tag('label',self.Title))
        
    def queueCmd(self,setting):
        self.queue.put(setting)
           
    def getControls(self):
        return self.category.getControls()
        
    def getTitleContent(self):
        return self.Menucategory
    
    def getSettings(self) :
        return self.settings
    
    def getCategory(self):
		return self.category

    
class Setting():
	CONTROL = None
	DIALOGHEADER = "" #"override dialog header"
	ERRORTEXT = "" #"Override Error Text here"
	OKTEXT = "" #"override Ok Text"
	BADUSERENTRYTEXT = ""
	ADDON     = Addon( __addonID__ )
	
	def __init__(self) :
		self.control = self.CONTROL
		self.userValue = None
		self.xbianValue = None
		self.clickId = self.control.getClickID()
		self.queue = None
		self.onInit()
		
	
	def onInit(self) :
		#Override this method if you need to do something on init
		#don't override __init__
		pass
	
	def addQueue(self,queue):
		self.queue = queue
	
	def setSetting(self,id,value):
		self.ADDON.setSetting(id,value)
	
	def getSetting(self,id):
		return self.ADDON.getSetting(id)
	
	def onClick(self,ctrlId):
		if ctrlId == self.clickId :
			self.updateFromUser()
			
	def getControl(self) :
		return self.control
		
	def getControlValue(self):
		return self.control.getValue()
	
	def setControlValue(self,value) :
		self.control.setValue(value)
	
	def getUserValue(self):
		#this method must be overrided if user can modify value
		#must create the user interface
		return None
	
	def checkUserValue(self,value):
		#this method can be overrided if user can modify value
		#check validity of user Value
		#return True if data is valid
		#False either
		return True
	
	def updateFromUser(self):
		self.userValue = self.getUserValue()
		if self.userValue and self.checkUserValue(self.userValue) :
			ok = True
			if self.getSetting('confirmationonchange') != '0' :
				if not dialog.yesno(self.DIALOGHEADER,'Apply Change') :
					ok = False
					self.updateFromXbian()
			if ok :
				self.QueueSetXbianValue(self.userValue)
				self.setControlValue(self.userValue)
				return True
		elif self.userValue and not self.checkUserValue(self.userValue) :
			dialog.ok(self.DIALOGHEADER,self.BADUSERENTRYTEXT)
			self.setControlValue(self.xbianValue)
	
	def updateFromXbian(self):
		#dialog.ok("update from xbian",ADDON.getSetting('notifyonerror'))
		self.xbianValue = self.getXbianValue()
		self.setControlValue(self.xbianValue)
		
	def getXbianValue(self):
		#this method must be overrided
		#get the default Xbian Value
		return None
	
	def QueueSetXbianValue(self,value) :
		if self.queue :
			self.queue.put([self,value])
	
	def ThreadSetXbianValue(self,value) :
		if 	not self.setXbianValue(value) :
			if self.getSetting('notifyonerror') != '0' :
				xbmc.executebuiltin("Notification(%s,%s)"%(self.DIALOGHEADER,self.ERRORTEXT))
			self.updateFromXbian()
		elif self.getSetting('notifyonsuccess') == '1' :
				xbmc.executebuiltin("Notification(%s,%s)"%(self.DIALOGHEADER,self.OKTEXT))
		
	def setXbianValue(self,value):
		#this method must be overrided
		#get the default Xbian Value
		return True
		
