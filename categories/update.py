import os
import subprocess
import time

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig

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
    
    def onInit(self) :
        self.canUpdate = True
        
    def getUserValue(self):
        print 'coco update' + str(self.getControlValue())
        return ['update',self.getControlValue()]
        
    def getXbianValue(self):
        rc =xbianConfig('updates','check')
        if not rc or rc[0] == '-1' :
            self.canUpdate = False
            return 'Something went wrong'         
        elif rc[0] == '0' :
            self.canUpdate = False
            return 'Your system is up to date'
        else :
            self.canUpdate = True
            return rc[0]
                            
    def setXbianValue(self,value):
        print 'coco setupdate' + str(value)
        xbmcgui.Dialog().ok(self.DIALOGHEADER,'here i do the upgrade')
        #log = '/home/belese/log'
        #daemon = UpdateDaemon('/home/belese/daemon-example.pid' ,stdout=log, stderr=log)
        #f = open(log, 'a+')
        #f.close()
        #daemon.start()
        updateScript = os.path.join(BASE_RESOURCE_PATH,'lib','daemonUpdater.py')
        print updateScript 
        updateDaemon = subprocess.Popen(updateScript)
        print updateDaemon.communicate()
        #updateDaemon = threading.Thread(name='daemonUpdater', target=self.daemonUpdater)
        #updateDaemon.setDaemon(True)
        #updateDaemon.start()
        return True  
        
   

class update(Category) :
    TITLE = 'Update'
    SETTINGS = [updateLabel,updateAvailable]
    


