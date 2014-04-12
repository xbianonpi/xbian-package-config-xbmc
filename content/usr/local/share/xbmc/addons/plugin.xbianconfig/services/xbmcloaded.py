from resources.lib.service import service
import os

class reportloaded(service):
    def onStart(self):
        os.system("/usr/bin/sudo /sbin/start -n xbmc-loaded")
        print 'XBian : notify upstart'
