# -*- coding: cp1252 -*-

__script__       = "Unknown"
__plugin__       = "xbian-config"
__addonID__      = "plugin.xbianconfig"
__author__       = "Belese (http://www.xbian.org)"
__url__          = "http://www.xbian.org"
__credits__      = "XBian"
__platform__     = "xbmc media center"
__date__         = "30-11-2012"
__version__      = "0.0.1"

import os
import sys
import Queue
import traceback
import urllib
from resources.lib.utils import *
import resources.lib.translation
_ = resources.lib.translation.language.ugettext


# xbmc modules
import xbmc
import xbmcgui
from xbmcaddon import Addon


#addon module
ADDON     = Addon( __addonID__ )

ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString


ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CATEGORY_PATH = 'categories'

SKIN_DIR = xbmc.getSkinDir()
LOCK_FILE = os.path.join('/','tmp','.xbian_config_python')





class xbianSettingCommon :
    def __init__(self) :
        xbmc.log('XBian : XBian-config started')
        from resources.lib.updateworker import Updater
        from resources.lib.xbianconfig import xbianConfig
        if xbianConfig('updates','progress')[0] != '1':
            setvisiblecondition('aptrunning',False)            
        else :
            setvisiblecondition('aptrunning',True)
        self.checkReboot = False
        self.CmdQueue = Queue.Queue()
        self.updateThread = Updater(self.CmdQueue)
        self.updateThread.start()
        self.onInit()
        
    def onInit(self):
        pass

    def onClean(self):
        pass

    def onShown(self):
        pass

    def _checkIsRunning(self) :
        if os.path.isfile(LOCK_FILE) :
            xbmcgui.Dialog().ok('XBian-config','XBian-config is still running','Please wait...')
            return False
        open(LOCK_FILE,'w').close()
        return True

    def clean(self) :
        self.updateThread.stop()
        self.onClean()
        if os.path.isfile(LOCK_FILE) :
            os.remove(LOCK_FILE)
        if self.checkReboot :
            from resources.lib.xbianconfig import xbianConfig            
            rebootneeded = xbianConfig('reboot')
            updateinprogress = xbianConfig('updates','progress')
            if rebootneeded and rebootneeded[0] == '1' and updateinprogress[0] == '0' and xbmcgui.Dialog().yesno('XBian-config',_('xbian-config.main.reboot_question')):
                xbmc.executebuiltin('Reboot')
                
    def show(self) :        
        if self._checkIsRunning() :
            self.onShow()                       
        self.clean()

class xbianSettingWindow(xbianSettingCommon) :
    def onInit(self) :
        from resources.lib.xbianWindow import XbianWindow
        import categories        
        self.window = None
        self.category_list = categories.__all__
        self.total = len(self.category_list)
        self.category_list_instance = []
        self.finished = 0
        self.globalProgress = 0
        self.stop = False
        self.checkReboot = True
        self.wait = xbmcgui.DialogProgress()
        self.wait.create('%s %s'%(_("distribution"),_('xbian-config.main.title')),_('xbian-config.common.pleasewait'))
        self.wait.update(0)        
        self.window = XbianWindow('SettingsXbianInfo.xml',ROOTDIR)        

    def onClean(self) :
        if self.wait :
            self.wait.close()

    def onShow(self) :              
        for i,module in enumerate(self.category_list) :
             if self.wait.iscanceled():
                self.stop = True
                break
             self.globalProgress =  int((float(self.finished)/(self.total)) * 100)
             self.update_progress(module.split('_')[1],'    %s'%_('xbian-config.common.initialisation'),0)
             catmodule = __import__('%s.%s'%(CATEGORY_PATH,module), globals(), locals(), [module])
             modu = getattr(catmodule,module.split('_')[-1])
             catinstance = modu(self.CmdQueue,self.update_progress)
             self.finished += 1
             if catinstance.TITLE :
                 try :
                     self.window.addCategory(catinstance)
                 except:
                     xbmc.log('XBian : Cannot add category: %s \n%s'%(str(module),str(sys.exc_info())))

        if not self.stop :
            #really don't know why, all others are ok, but skindir have to be global???
            global SKIN_DIR            
            if not os.path.isfile(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianInfo.template')) :
                SKIN_DIR = 'Default'                
            self.window.doXml(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianInfo.template'))
            self.wait.close()
            self.wait = None            
            self.window.doModal()            
            xbmc.log('XBian : XBian-config-python closed')

    def update_progress(self,categoryname,settingName,perc) :
        perc = self.globalProgress + int(perc/self.total)
        self.wait.update(perc,'%s %s...'%(_('xbian-config.common.loading'),categoryname),'   %s'%settingName)

class xbianSettingDialog(xbianSettingCommon) :
    def onInit(self) :        
        from resources.lib.utils import dialogWait
        self.wait = dialogWait(_('xbian-config.common.loading'),_('xbian-config.common.pleasewait'))
        self.wait.show()
        from resources.lib.xbianDialog import XbianDialog
        self.title = ''
        self.settings = []                
        self.window = XbianDialog('SettingsXbianDialog.xml',ROOTDIR)

    def createDialog(self,title,settings,checkReboot=False) :
        self.title = title
        self.settings = settings
        self.checkReboot = checkReboot

    def onClean(self) :
        if self.wait :
            self.wait.close()

    def onShow(self) :
         self.window.initialise(self.title,self.CmdQueue)
         for setting in self.settings :
             self.window.addSetting(self._import_class(setting))                         
         global SKIN_DIR
         if not os.path.isfile(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianDialog.template')) :
                SKIN_DIR = 'Default'                
         self.window.doXml(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianDialog.template'))
         self.wait.close()
         self.wait = None
         self.window.doModal()
         

    def _import_class(self,className) :
        name = className.split('.')
        settingmodule = __import__(".".join(name[:-1]), globals(), locals(),[name[-2]])
        return getattr(settingmodule,name[-1])

class xbianSettingWizzard :
    def show(self):
        from resources.lib.xbianWizardDialog import wizardDialog
        wizardDialog('WizzardDialog.xml',ROOTDIR).doModal()        

def get_params():
        param=[]
        if len(sys.argv)>=1:
           params=sys.argv[1]
           cleanedparams=params.replace('?','')
           if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
           pairsofparams=cleanedparams.split('&')
           param={}
           for i in range(len(pairsofparams)):
                  splitparams={}
                  splitparams=pairsofparams[i].split('=')
                  if (len(splitparams))==2:
                         param[splitparams[0]]=splitparams[1]
        return param



################MAIN##################
try :
    params=get_params()
    mode=int(params["mode"])
except :
    mode = None

if mode==None or mode==0 :
    #full settings windows mode
    win = xbianSettingWindow()
    try :
        #win = xbianSettingWindow()
        win.show()
    except :
        win.clean()
        xbmc.log('Exception in xbianSettingWindow %s'%str(traceback.print_exc()),xbmc.LOGERROR)
elif mode==1 :
    #show dialog settings
    #plugin.xbianconfig?mode=1&title=foo&settings=categories.system.network,categories.vc1license,... (url_quoted text)
    try :
        print params
        win = xbianSettingDialog()
        win.createDialog(urllib.unquote_plus(params["title"]),urllib.unquote_plus(params["settings"]).split(','))
        win.show()
    except :
        win.clean()
        xbmc.log('Exception in xbianSettingDialog %s'%str(traceback.print_exc()),xbmc.LOGERROR)
elif mode==2 :
    #show wizard dialog
    #plugin.xbianconfig?mode=2
    try :
        win = xbianSettingWizzard()
        win.show()
    except :
        xbmc.log('Exception in xbianSettingWizard %s'%str(traceback.print_exc()),xbmc.LOGERROR)
else :
    xbmc.log('XBian-config : Unknown mode : %d'%mode,xbmc.LOGERROR)

