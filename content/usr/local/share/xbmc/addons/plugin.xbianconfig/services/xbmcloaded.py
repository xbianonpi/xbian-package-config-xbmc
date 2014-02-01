from resources.lib.service import service
import os

class reportloaded(service):
    def onStart(self):
        print 'XBian : notify upstart'
        os.system("/usr/bin/sudo /sbin/start -n xbmc-loaded")
