# -*- coding: cp1252 -*-

__script__       = "Unknown"
__plugin__       = "xbian-config"
__addonID__      = "plugin.xbianconfig"
__author__       = "Belese(http://www.xbian.org)"
__url__          = "http://www.xbian.org"
__credits__      = "Xbian"
__platform__     = "xbmc media center"
__date__         = "30-11-2012"
__version__      = "0.0.1"


import os
import itertools
import fnmatch
import shutil
import threading
import Queue

# xbmc modules
import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon

#xbmcguie
from resources.lib.xbmcguie import window

from resources.lib.updateworker import Updater
#addon module 
ADDON     = Addon( __addonID__ )
Language  = ADDON.getLocalizedString
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString


ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )

CmdQueue = Queue.Queue()
updateThread = Updater(CmdQueue)
updateThread.start()

try :
	a = window.WindowSkinXml('SettingsXbianInfo.xml',ROOTDIR)
	from categories.system import system
	systemcat = system(CmdQueue)     
	a.addCategory(systemcat)
	from categories.preference import preference
	pref = preference(CmdQueue)     
	a.addCategory(pref)

	a.doXml(os.path.join(ROOTDIR,'resources','skins','Default','720p','SettingsXbianInfo.template'))
	a.doModal()
except :
	print 'Exception in plugin-xbianconfig'
finally :
	updateThread.stop()

