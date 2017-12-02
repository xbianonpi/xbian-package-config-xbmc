import os
import xbmc
import pyinotify

from services.firstrun import firstrun
from services.xbianworker import xbianworker

print 'XBian services started (%s)' % xbmc.__version__

__addonID__ = "plugin.xbianconfig"

# Files and/or folders which are be watched by inotify
PERIODICSETTING = '/etc/apt/apt.conf.d/20auto-upgrade'
UPDATEREPO      = '/usr/local/sbin/xbian-update-repo'
RUNPATH         = '/run'
REBOOTREQUIRED  = 'reboot-required'
FORCEREFRESH    = 'force-refresh'
SETTINGPATH     = '/etc/default'

# Folder we write/expect status/config files
MASTERPATH      = xbmc.translatePath("special://userdata/addon_data/%s/" % __addonID__)
ADDONPATH       = xbmc.translatePath("special://profile/addon_data/%s/" % __addonID__)

# Statusfiles from backup image and home folder process
XBIANCOPY       = 'xbiancopy'
BACKUPHOME      = 'backuphome'

IMAGESTATUS     = os.path.join(MASTERPATH, XBIANCOPY)
HOMESTATUS      = os.path.join(MASTERPATH, BACKUPHOME)

MSG4KODI        = 'msg4kodi'
MSG4KODIFILE1   = os.path.join(MASTERPATH, MSG4KODI)
MSG4KODIFILE2   = os.path.join('/run/splash', MSG4KODI)

onRun = os.path.join('/', 'tmp', '.xbian_config_python')
if os.path.isfile(onRun):
    os.remove(onRun)
onWiz = os.path.join('/', 'tmp', '.xbian_wizard')
if os.path.isfile(onWiz):
    os.remove(onWiz)

firstrun().onStart()

worker = xbianworker()

class eventHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        print event
        if event.name == REBOOTREQUIRED:
            worker.onStatusChanged('reboot')
        elif event.name == FORCEREFRESH:
            worker.onStatusChanged('refresh')

    def process_IN_DELETE(self, event):
        print event
        if event.name == REBOOTREQUIRED:
            worker.onStatusChanged('noreboot')
        elif 'hide.' in event.name:
            worker.onStatusChanged(event.name)

    def process_IN_MODIFY(self, event):
        print event
        if event.pathname == PERIODICSETTING or event.name == 'xbian-snap' or event.name == 'notifywhenbusy':
            worker.onStatusChanged('setting')
        elif event.name == MSG4KODI:
            worker.onStatusChanged(MSG4KODI, event.pathname)
        elif event.pathname == UPDATEREPO:
            worker.onStatusChanged('upgrade')
        elif event.pathname == IMAGESTATUS:
            worker.onStatusChanged(XBIANCOPY, IMAGESTATUS)
        elif event.pathname == HOMESTATUS:
            worker.onStatusChanged(BACKUPHOME, HOMESTATUS)
        elif 'hide.' in event.name:
            worker.onStatusChanged(event.name)
        elif event.name == REBOOTREQUIRED:
            worker.onStatusChanged('reboot')
        elif event.name == FORCEREFRESH:
            worker.onStatusChanged('refresh')

    def process_IN_MOVED_TO(self, event):
        print event
        if event.pathname == PERIODICSETTING or event.name == 'xbian-snap':
            worker.onStatusChanged('setting')
        elif event.name == MSG4KODI:
            worker.onStatusChanged(MSG4KODI, event.pathname)

wm = pyinotify.WatchManager()

notifier = pyinotify.ThreadedNotifier(wm, eventHandler())

wm.add_watch(SETTINGPATH, pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO)
wm.add_watch(RUNPATH, pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO)
wm.add_watch(MASTERPATH, pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY)
if MASTERPATH != ADDONPATH:
    print 'XBian : add profile path %s' % ADDONPATH
    wm.add_watch(ADDONPATH, pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY)
wm.add_watch('/run/splash', pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY)
wm.watch_transient_file(PERIODICSETTING, pyinotify.IN_MODIFY, eventHandler)
wm.watch_transient_file(UPDATEREPO, pyinotify.IN_MODIFY, eventHandler)

notifier.start()

if os.path.isfile(os.path.join(RUNPATH, REBOOTREQUIRED)):
    worker.onStatusChanged('reboot')

if os.path.isfile(UPDATEREPO):
    worker.onStatusChanged('upgrade')

if os.path.isfile(MSG4KODIFILE1):
    worker.onStatusChanged(MSG4KODI, MSG4KODIFILE1)

if not os.path.isfile(IMAGESTATUS):
    open(IMAGESTATUS, 'w').close()
worker.onStatusChanged(XBIANCOPY, IMAGESTATUS)

if not os.path.isfile(HOMESTATUS):
    open(HOMESTATUS, 'w').close()
worker.onStatusChanged(BACKUPHOME, HOMESTATUS)

worker.onStart()

notifier.stop()

print 'XBian services finished'
