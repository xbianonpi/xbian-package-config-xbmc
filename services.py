import xbmc
import xbmcgui


from services.firstrun import firstrun
firstrun_thread = firstrun()     
firstrun_thread.onStart()

from services.upgrade import upgrade
upgrade_thread = upgrade()     
upgrade_thread.onStart()

from services.resize import resize
resize_thread = resize()     
resize_thread.onStart()

