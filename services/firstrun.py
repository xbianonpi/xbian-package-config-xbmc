import xbmcgui
import xbmc
from resources.lib.service import service
from xbmcaddon import Addon
import os

__addonID__ = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )

class firstrun(service):
    def onStart(self):
        #check if first run        
        firstlock = os.path.join(ADDON_DATA,'.firstrun')
        if not os.path.isfile(firstlock) :
			ADDON.setSetting('advancedmode','0')
			ADDON.setSetting('notifyonerror','1')
			ADDON.setSetting('notifyonsuccess','1')
			ADDON.setSetting('confirmationonchange','1')
        	#set default preference:			
			xbmcgui.Dialog().ok('Welcome to XBian','Thanks to have choose XBian','You can configure it, go to','System -> XBian')
			open(firstlock,'w').close()			
