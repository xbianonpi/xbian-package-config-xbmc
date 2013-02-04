import xbmc
import xbmcgui

from services.upgrade import upgrade
upgrade_thread = upgrade()     
upgrade_thread.onStart()

from services.resize import resize
resize_thread = resize()     
resize_thread.onStart()
