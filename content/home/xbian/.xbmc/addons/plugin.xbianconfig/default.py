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
import itertools
import fnmatch
import shutil
#import threading
import Queue
import subprocess

# xbmc modules
import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon

#xbmcguie
from resources.lib.xbianWindow import XbianWindow
from resources.lib.updateworker import Updater
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import dialogWait

import categories

#addon module 
ADDON     = Addon( __addonID__ )
Language  = ADDON.getLocalizedString
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString


ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CATEGORY_PATH = 'categories'

SKIN_DIR = xbmc.getSkinDir()

try:
   with open(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianInfo.template')): pass
except IOError:
   SKIN_DIR = 'Default'

class xbian_config_python :
    def __init__(self) :              
        xbmc.log('XBian : XBian-config-python started')
        self.onRun = os.path.join('/','tmp','.xbian_config_python')
        if os.path.isfile(self.onRun) :
            xbmcgui.Dialog().ok('XBian-config','XBian-config is still running','Please wait...')
        else :      
            open(self.onRun,'w').close()            
            try :            
                self.CmdQueue = Queue.Queue()
                self.updateThread = Updater(self.CmdQueue)                                
                self.window = XbianWindow('SettingsXbianInfo.xml',ROOTDIR)
                self.category_list = categories.__all__                
                self.category_list_instance = []
                self.finished = 0
                self.globalProgress = 0
                self.stop = False                    
                self.wait = xbmcgui.DialogProgress()
                self.wait.create('Loading Settings','Inititalisation')
                self.wait.update(0)
                
                self.total = len(self.category_list)                
                
                for i,module in enumerate(self.category_list) :
                    print 'Load %s'%module
                    self.globalProgress =  int((float(self.finished)/(self.total)) * 100)
                    self.update_progress(module.split('_')[1],'   initialise',0)                        
                    catmodule = __import__('%s.%s'%(CATEGORY_PATH,module), globals(), locals(), [module])                        
                    modu = getattr(catmodule,module.split('_')[1])                                                        
                    catinstance = modu(self.CmdQueue,self.update_progress)                                        
                    self.finished += 1                                        
                    try :                    
                       self.window.addCategory(catinstance)                            
                    except:
                       xbmc.log('XBian : Cannot add category: %s \n%s'%(str(module),str(sys.exc_info())))                                            
                        
                if not self.stop :
                    #self.wait.update(90,'Generate Windows')
                    self.window.doXml(os.path.join(ROOTDIR,'resources','skins',SKIN_DIR,'720p','SettingsXbianInfo.template'))
                    self.wait.close()                    
                    self.updateThread.start()
                    self.window.doModal() 
                    xbmc.log('XBian : XBian-config-python closed')
                    self.window.stopRequested = True 
                    progress = dialogWait('XBian config','Checking if reboot is needed...')
                    progress.show() 
                    rebootneeded = xbianConfig('reboot')
                    progress.close()
                    if rebootneeded and rebootneeded[0] == '1' :
                        rebootneeded = xbianConfig('updates','progress')
                        if rebootneeded and rebootneeded[0] == '0' :
                            if xbmcgui.Dialog().yesno('XBian-config','A reboot is needed','Do you want to reboot now?') :
                                #reboot
                                xbmc.executebuiltin('Reboot')       
            except :
                self.window.stopRequested = True            
                try :
                    #close wait dialog if something was wrong
                    self.wait.close()
                except :
                    pass
                xbmcgui.Dialog().ok('XBian-config','Something went wrong while creating the window','Please contact us on www.xbian.org for further support')
                xbmc.log('XBian : Cannot create Main window: %s'%(str(sys.exc_info())))                            
            finally :                
                self.updateThread.stop()
                os.remove(self.onRun)                
                del(self.window)
        
        
    def update_progress(self,categoryname,settingName,perc) :                
        perc = self.globalProgress + int(perc/self.total)  
        print 'Progress %s %s : %d'%(categoryname,settingName,perc)          
        self.wait.update(perc,'Loading %s...'%categoryname,'   %s'%settingName)        
                         
xbian_config_python()
