from resources.lib.service import service
import os

class reportloaded(service):
    def onStart(self):
        os.system("sudo start -n xbmc-loaded")
