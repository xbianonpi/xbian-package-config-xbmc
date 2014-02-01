import os

onRun = os.path.join('/','tmp','.xbian_config_python')
if os.path.isfile(onRun) :
	os.remove(onRun)

from services.xbmcloaded import reportloaded
upgrade_thread = reportloaded()
upgrade_thread.onStart()

from services.firstrun import firstrun
firstrun_thread = firstrun()
firstrun_thread.onStart()

from services.upgrade import upgrade
upgrade_thread = upgrade()
upgrade_thread.onStart()

