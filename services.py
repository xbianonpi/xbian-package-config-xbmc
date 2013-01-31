import xbmc
import xbmcgui

from services.upgrade import upgrade
upgrade_thread = upgrade()     
upgrade_thread.onStart()
