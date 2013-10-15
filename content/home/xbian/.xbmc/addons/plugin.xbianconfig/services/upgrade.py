import os
import xbmc
import xbmcgui
from xbmcaddon import Addon
from resources.lib.service import service
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import dialogWait,setSetting,getSetting
from datetime import datetime, timedelta

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )

class upgrade(service):
    def onInit(self):
        self.StopRequested = False
        self.xbianUpdate = False
        self.packageUpdate = False
        self.rebootNeeded = False
        self.rebootNoCheck = False
        print 'XBian : upgrade service started'
    
    def onAbortRequested(self):
        os.system('sudo kill $(cat /run/lock/xbian-config) &>/dev/null')
        self.StopRequested = True
        
    def onScreensaverActivated(self):
        print 'XBian : screensaver activated'
        if not xbmc.Player().isPlaying() and (getSetting('lastupdatecheck') == None  or getSetting('lastupdatecheck') < datetime.now() - timedelta(days=1)):
            print 'XBian : Checking for update'
            #check if new upgrade avalaible
            rc =xbianConfig('updates','list','upgrades')
            if rc and rc[0] == '-3' :
                rctmp = xbianConfig('updates','updatedb')
                if rctmp and rctmp[0] == '1' :
                     rc =xbianConfig('updates','list','upgrades')
                else :
                    rc[0]= '0'
            if rc and rc[0] not in ('0','-2') :
                retval = rc[0].split(';') 
                self.xbianUpdate = retval[3]            
           
           #check if new update package avalaible
            rc =xbianConfig('updates','list','packages')
            if rc and rc[0] not in ('0','-2') :
                self.packageUpdate = True
            setSetting('lastupdatecheck',datetime.now())

    def onIdle(self):
        if self.rebootNoCheck:
            return

        if os.path.isfile('/tmp/.xbian_config_python'):
            return 

        rebootneeded = xbianConfig('reboot')

        if rebootneeded and rebootneeded[0] == '1' :
            rebootneeded = xbianConfig('updates','progress')
            if rebootneeded and rebootneeded[0] == '0' :
                if xbmcgui.Dialog().yesno('XBian-config','A reboot is needed','Do you want to reboot now?') :
                    #reboot
                    os.system('sudo reboot')
                    xbmc.executebuiltin("XBMC.Quit()")
                    self.rebootNeeded = True
                else:
                    self.rebootNoCheck = True

    def onScreensaverDeactivated(self):
        self.onIdle()
        if self.rebootNeeded:
            return
        else:
            if self.xbianUpdate :
                xbmc.executebuiltin("Notification(XBian Upgrade,A new version (%s) of XBian is out)"%(self.xbianUpdate))            
                self.xbianUpdate = False            
            if self.packageUpdate :
                xbmc.executebuiltin("Notification(Packages Update,Some XBian package can be updated)")
                self.packageUpdate = False

    def onStart(self):
        #check if Xbian is upgrading
        if os.path.isfile('/var/lock/.upgrades') :
            if xbianConfig('updates','progress')[0] == '1':
                dlg = dialogWait('XBian Update','Please wait while updating')
                dlg.show()
                while not self.StopRequested and xbianConfig('updates','progress')[0] == '1':
                    xbmc.sleep(2000)
                dlg.close()
                if self.StopRequested :
                    return              
        
            xbmc.executebuiltin("Notification(%s,%s)"%('XBian Upgrade','XBian was updated successfully'))
            os.remove('/var/lock/.upgrades')
        
        #check is packages is updating
        if os.path.isfile('/var/lock/.packages') :
            if xbianConfig('updates','progress')[0] == '1':
                dlg = dialogWait('XBian Update','Please wait while updating')
                dlg.show()
                while not self.StopRequested and xbianConfig('updates','progress')[0] == '1':
                    xbmc.sleep(2000)
                dlg.close()
                if self.StopRequested :
                    return              
            xbmc.executebuiltin("Notification(%s,%s)"%('Package Update','Package was updated successfully'))
            os.remove('/var/lock/.packages')
        if xbianConfig('updates','progress')[0] != '1':
            xbmc.executebuiltin('Skin.Reset(aptrunning)')
        #for those one who deactivate its screensaver, force check every 10 days
        if getSetting('lastupdatecheck') != None and getSetting('lastupdatecheck') < datetime.now() - timedelta(days=10):
            self.onScreensaverActivated()
            self.onScreensaverDeactivated()
        while not self.StopRequested and not self.rebootNeeded: #End if XBMC closes
            self.onIdle()
            self.x = 0
            while not self.rebootNeeded and not self.StopRequested and self.x < 600:
                xbmc.sleep(500) #Repeat (ms) 
                self.x = self.x + 1

        print 'XBian : upgrade service finished'

