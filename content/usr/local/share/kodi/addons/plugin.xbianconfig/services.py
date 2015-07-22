import os

from services.firstrun import firstrun
from services.upgrade import upgrade


onRun = os.path.join('/', 'tmp', '.xbian_config_python')
if os.path.isfile(onRun):
    os.remove(onRun)

firstrun_thread = firstrun()
firstrun_thread.onStart()

upgrade_thread = upgrade()
upgrade_thread.onStart()
