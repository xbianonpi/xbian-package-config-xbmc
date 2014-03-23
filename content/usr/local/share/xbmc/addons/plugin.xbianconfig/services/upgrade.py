import os
import xbmc
import xbmcgui
from xbmcaddon import Addon
from resources.lib.service import service
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
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
        self.inScreenSaver = False
        rc = xbianConfig('updates','enableauto')
        if rc and rc[0]=='1' :
            self.enableauto = True
        else :
            self.enableauto = False
        try :
            self.deltaCheck = int(xbianConfig('updates','autoinventory')[0].split(' ')[1])
        except :
            self.deltaCheck = 100
        print 'XBian : upgrade service started'

    def onAbortRequested(self):
        print 'XBian : abort requested'

        try:
            os.system('/bin/kill $(cat /run/lock/xbian-config) >/dev/null 2>&1 && sudo /bin/kill $(cat /run/lock/xbian-config) >/dev/null 2>&1 || :')
        except:
            pass

        self.StopRequested = True

    def onScreensaverActivated(self):        
        self.inScreenSaver = True

        if self.enableauto  :
            return

        if not xbmc.Player().isPlaying()  and (getSetting('lastupdatecheck')==None or getSetting('lastupdatecheck') < (datetime.now() - timedelta(days=self.deltaCheck))):
            #check if new upgrades avalaible           
            rc =xbianConfig('updates','list','packages',forcerefresh=True)
            if rc and rc[0] == '-3' :                
                rctmp = xbianConfig('updates','updatedb')
                if rctmp and rctmp[0] == '1' :
                    rc =xbianConfig('updates','list','packages',forcerefresh=True)
                    #refresh also package cache
                    pkglist = xbianConfig('packages','list',forcerefresh=True)
                    for pkg in pkglist :
                        xbianConfig('packages','list',pkg.split(',')[0],forcerefresh=True)
                else :
                    rc[0]= '0'
            
            if rc and rc[0] and len(rc[0])>2  : 
                self.packageUpdate = True
                print 'XBian : new updates available'

            setSetting('lastupdatecheck',datetime.now())

    def showRebootDialog(self):
        if self.inScreenSaver or os.path.isfile('/tmp/.xbian_config_python'):
            return

        stillrunning = xbianConfig('updates','progress')
        if stillrunning and stillrunning[0] == '1' :
            return

        self.rebootNeeded = False

        if xbmcgui.Dialog().yesno('XBian-config',_('xbian-config.main.reboot_question')):
            xbmc.executebuiltin("XBMC.Restart()")
        else:
            self.rebootNoCheck = True

    def onIdle(self):
        if self.rebootNoCheck or os.path.isfile('/tmp/.xbian_config_python') or self.rebootNeeded:
            return

        rebootneeded = xbianConfig('reboot')
        if rebootneeded and rebootneeded[0] == '1' :
            self.rebootNeeded = True
            self.showRebootDialog()

    def onScreensaverDeactivated(self):
        self.inScreenSaver = False
        if self.rebootNeeded:
            self.showRebootDialog()

        else:
            if self.packageUpdate :
                xbmc.executebuiltin("Notification(Packages Update,Some XBian package can be updated)")
                self.packageUpdate = False

    def onStart(self):
        #check is packages is updating
        if os.path.isfile('/var/lock/.packages') :
            if xbianConfig('updates','progress')[0] == '1':
                dlg = dialogWait('XBian Update','Please wait while updating')
                dlg.show()
                while not self.StopRequested and xbianConfig('updates','progress')[0] == '1':
                    xbmc.sleep(1000)
                dlg.close()
                if self.StopRequested :
                    return
            xbmc.executebuiltin("Notification(%s,%s)"%('Package Update','Updates installed successfully'))
            os.remove('/var/lock/.packages')

        if xbianConfig('updates','progress')[0] != '1':
            setvisiblecondition('aptrunning',False)            

        #for those one who deactivate its screensaver, force check every deltaCheck days
        
        
        if not self.enableauto and getSetting('lastupdatecheck') != None and getSetting('lastupdatecheck') < datetime.now() - timedelta(days=self.deltaCheck):
            print 'XBian : screensaver is disabled, running internal updates'
            self.onScreensaverActivated()
            self.onScreensaverDeactivated()

        while not self.StopRequested: #End if XBMC closes
            self.onIdle()
            self.x = 0
            while not self.StopRequested and self.x < 600:
                xbmc.sleep(500) #Repeat (ms) 
                self.x = self.x + 1
        print 'XBian : upgrade service finished'

