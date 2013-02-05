import xbmcgui
import xbmc
from resources.lib.service import service
from xbmcaddon import Addon

__addonID__ = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )

class firstrun(service):
    def onStart(self):
        #check if first run
        print 'fisrt run'
        a = ADDON.getSetting('firstxbianrun')
        if not a :
			#set default preference:
			ADDON.setSetting('advancedmode','0')
			ADDON.setSetting('notifyonerror','1')
			ADDON.setSetting('notifyonsuccess','1')
			ADDON.setSetting('confirmationonchange','1')			
			xbmcgui.Dialog().ok('Welcome to XBian','Thanks to have choose xbian','bla bla bla')
			ADDON.setSetting('firstxbianrun','true')
