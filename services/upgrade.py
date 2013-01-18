import os
import time
import xbmc
from xbmcaddon import Addon
from resources.lib.service import service
from resources.lib.updater import updater

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )

class upgrade(service):
    def onInit(self):
        self.StopRequested = False
    
    def onAbortRequested(self):
        self.StopRequested = True
            
    def onStart(self):
        updt = updater()
        rc = updt.isUpgraded()
        if rc != None :
            if rc : 
                xbmc.executebuiltin("Notification('Upgrade','Your system is upgraded')")
            else :
                xbmc.executebuiltin("Notification('Upgrade','Something went wrong while upgrading')") 
                    
