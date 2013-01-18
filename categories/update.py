import os
import subprocess
import time

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.updater import updater
import xbmcgui,xbmc
from xbmcaddon import Addon

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )



class updateLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Update'))

class updateAvailable(Setting) :
    CONTROL = ButtonControl(Tag('label','Update :'))
    DIALOGHEADER = "Xbian Update"
    ERRORTEXT = "Error upgrading"
    OKTEXT = "Upgrade ok"
    APPLYTEXT = "Do you want to upgrade Xbian"
    
    
    def onInit(self):
		self.forceUpdate=True
		    
    def getUserValue(self):
        return self.getControlValue()
        
    def getXbianValue(self):
        rc =xbianConfig('updates','check')
        if not rc or rc[0] == '-1' :
            self.canBeUpdated = False
            return 'Something went wrong'         
        elif rc[0] == '0' :
            self.canBeUpdated = False
            return 'Up-to-date'
        else :
            self.canBeUpdated = True
            return rc[0]
                            
    def setXbianValue(self,value):        
        print 'coco setupdate' + str(value)
        progress = updater(True)
        return progress.isUpgraded()
        
		

class update(Category) :
    TITLE = 'Update'
    SETTINGS = [updateLabel,updateAvailable]
    


