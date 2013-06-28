__addonID__      = "plugin.xbianconfig"

import os
import xbmcgui
import xbmc
from xbmcaddon import Addon

ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR

SKIN_DIR = xbmc.getSkinDir()

try:
   with open(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianInfo.template')): pass
except IOError:
   SKIN_DIR = 'Default'

class WindowSkinXml(xbmcgui.WindowXML):   
    def __init__(self,strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False):
        self.xmlfile = os.path.join(strFallbackPath,'resources','skins',SKIN_DIR,'720p',strXMLname)
        self.controls = []
    
    def onInit(self):
        #set the windows instance in all xbmc control
        for control in self.controls :
            control.setWindowInstance(self)
    
    def doXml(self,template) :
        #must override this function
        #must create the xml
        pass
            
    def addControl(self,control):        
        self.controls.append(control)
        
    def onClick(self, controlID):
        for control in self.controls :
            control.click(controlID)
 
    def onFocus(self, controlID):
        for control in self.controls :
            control.focus(controlID)
    
    def close(self):
		#seem don't work
		#check after, have to call unFocus(0) when close
		self.onFocus(0)
		xbmcgui.WindowXML.close(self)

