import xbmcgui
import os
import subprocess
import time
import xbmc
from xbmcaddon import Addon
import xbmcgui

from resources.lib.xbianconfig import xbianConfig

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

class updater():
    def __init__(self,doUpgrade=False) :
        self.doUpgrade = doUpgrade
        self.dlg = updaterDlg('DialogUpgrade.xml',ROOTDIR)
        if os.path.exists('/var/lock/XBianUpdating') or self.doUpgrade:
            #must show update dialog
            self.dlg.doModal()
        
    def isUpgraded(self):
        return self.dlg.isUpgraded()

class updaterDlg(xbmcgui.WindowXMLDialog):         
    def isUpgraded(self) :
        self.upgraded = None
        if os.path.isfile('/tmp/resultCode') :
           resultFile = open('/tmp/resultCode','r')
           rc = resultFile.read()
           resultFile.close()
           os.remove('/tmp/resultCode')
           if rc[:1] == '1' :
                self.upgraded =  True
           else :
                self.upgraded =  False 
        elif ADDON.getSetting('updating') == 'true' :
			#dameon have crashed or XBian has reboot during install
			self.upgraded =  False 
			ADDON.setSetting('updating','false')
			
        return self.upgraded
 
    def onInit(self) :        
        if ADDON.getSetting('updating') != 'true' :
            #it's a new upgrade
            ADDON.setSetting('updating','true')
            rc =xbianConfig('updates','check')
            updateScript = os.path.join(BASE_RESOURCE_PATH,'lib','daemonUpdater.py')
            cmd = [updateScript,rc[0]]
            updateDaemon = subprocess.Popen(cmd)
            time.sleep(1)
                
        while os.path.exists('/var/lock/XBianUpdating') and not xbmc.abortRequested:
            #wait update has finished or xbmc restart
            time.sleep(0.5)
        if xbmc.abortRequested :
            #progress.update(0,'XBMC will restart','DO NOT UNPLUG PI')
            pass
        else :
            ADDON.setSetting('updating','false')
        self.close() 
