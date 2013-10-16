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
        self.inScreenSaver = False
        print 'XBian : upgrade service started'

    def onAbortRequested(self):
        print 'XBian : abort requested'
        self.StopRequested = True

        try:
            os.system('sudo kill $(cat /run/lock/xbian-config) &>/dev/null')
        except:
            pass

    def onScreensaverActivated(self):
        self.inScreenSaver = True

        rc =xbianConfig('updates','updates','enableauto')
        if rc and rc[0] == '1' :
            return

        print 'XBian : screensaver activated'
        #if not xbmc.Player().isPlaying() and (getSetting('lastupdatecheck') == None  or getSetting('lastupdatecheck') < datetime.now() - timedelta(days=1)):
        if not xbmc.Player().isPlaying() :
            print 'XBian : checking available package updates'
            #check if new upgrades avalaible
            rc =xbianConfig('updates','list','packages')
            if rc and rc[0] == '-3' :
                print 'XBian : refreshing apt inventory'
                rctmp = xbianConfig('updates','updatedb')
                if rctmp and rctmp[0] == '1' :
                    rc =xbianConfig('updates','list','packages')
                else :
                    rc[0]= '0'

            if rc and rc[0] == '1' : 
                self.packageUpdate = True
                print 'XBian : new updates available'

            setSetting('lastupdatecheck',datetime.now())

        print 'XBian : screensaver tasks finished'

    def showRebootDialog(self):
        if self.inScreenSaver or os.path.isfile('/tmp/.xbian_config_python'):
            return
        stillrunning = xbianConfig('updates','progress')
        if stillrunning and stillrunning[0] == '1' :
            return
        self.rebootNeeded = False
        if xbmcgui.Dialog().yesno('XBian-config','A reboot is needed','Do you want to reboot now?') :
            #reboot
            os.system('sudo reboot')
            xbmc.executebuiltin("XBMC.Quit()")
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
            xbmc.executebuiltin('Skin.Reset(aptrunning)')

        #for those one who deactivate its screensaver, force check every 10 days
        rc =xbianConfig('updates','updates','enableauto')
        if getSetting('lastupdatecheck') != None and getSetting('lastupdatecheck') < datetime.now() - timedelta(days=10) and rc and rc[0] == '0' :
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

