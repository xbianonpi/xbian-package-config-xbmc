import xbmc
import xbmcgui
import os

onRun = os.path.join('/','tmp','.xbian_config_python')
if os.path.isfile(onRun) :
	os.remove(onRun)
	
from services.firstrun import firstrun
firstrun_thread = firstrun()     
firstrun_thread.onStart()

from services.upgrade import upgrade
from services.upgrade import checkreboot
upgrade_thread = upgrade()     
upgrade_thread.onStart()
checkreboot_thread = checkreboot()
checkreboot_thread.onStart()
