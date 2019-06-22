import xbmc
import xbmcgui
from xbianconfig import xbianConfig
import time
import os
import shutil
from xbmcaddon import Addon
import pickle
import base64
import collections
import threading
from resources.lib.xbmcguie.tag import Tag
import resources.lib.translation
_ = resources.lib.translation.language.gettext


__addonID__ = "plugin.xbianconfig"
ADDON = Addon(__addonID__)
ADDON_DIR = ADDON.getAddonInfo("path")
ROOTDIR = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join(ROOTDIR, "resources")
ADDON_DATA = xbmc.translatePath("special://profile/addon_data/%s/" % __addonID__)


def setSetting(key, value):
    settingFile = open(os.path.join(ADDON_DATA, str(key)), 'w')
    pickle.dump(value, settingFile)
    settingFile.close()


def getSetting(key):
    settingPath = os.path.join(ADDON_DATA, str(key))
    if os.path.isfile(settingPath):
        return pickle.load(open(settingPath, 'r'))
    else:
        return None

HINTS = [ 'xbiancopy', 'backuphome', 'updates', 'upgradenotify' ]

def getHiddenHints():
    hidden = 0
    for hint in HINTS:
        if getSetting('hide.' + hint) == 1:
            hidden = hidden + 1
    return hidden

def enableAllHints():
    for hint in HINTS:
        setSetting('hide.' + hint, 0)

def getNumeric(header, default=None, min=False, max=False):
    dialog = xbmcgui.Dialog()
    cont = True
    while cont:
        rc = dialog.numeric(0, header, default)
        cont = False
        if min:
            if int(rc) < min:
                dialog.ok(header, _('Value must be greater than %d') % (min, ))
                cont = True
        if max:
            if int(rc) > max:
                dialog.ok(header, _('Value must be lower than %d') % (max, ))
                cont = True
    return rc


def remove(path):
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    else:
        return False
    return True


def getIp(header, default=None):
    dialog = xbmcgui.Dialog()
    return dialog.numeric(3, header, default)


def getFile(header, default=None):
    dialog = xbmcgui.Dialog()
    return dialog.browse(3, header, 'files')


def getText(header, default="", hidden=False):
    kb = xbmc.Keyboard(default, header, hidden)
    kb.doModal()
    if (kb.isConfirmed()):
        return kb.getText()
    else:
        return None


class PackageInfo:

    def __init__(self, header, name, versionl, versionr, sized, sizei, desc, dep):
        xbmc.executebuiltin('Skin.SetString(packageheader,Info : %s)' % header)
        xbmc.executebuiltin('Skin.SetString(packagename,Name : %s)' % name)
        xbmc.executebuiltin('Skin.SetString(packageversionr,Remote version : %s)' % versionr)
        if not versionl:
            versionl = 'Not installed'
        xbmc.executebuiltin('Skin.SetString(packageversioni,Local version : %s)' % versionl)
        xbmc.executebuiltin('Skin.SetString(packagesized,Download size : %s)' % sized)
        xbmc.executebuiltin('Skin.SetString(packagesizei,Installed size : %s)' % sizei)
        xbmc.executebuiltin('Skin.SetString(packagedesc,Description : %s)' % desc)
        if not dep:
            dep = 'None'
        xbmc.executebuiltin('Skin.SetString(packagedep,Dependency : %s)' % dep.replace(',', ''))
        self.dlg = xbmcgui.WindowXMLDialog('DialogPackageInfo.xml', ROOTDIR)
        self.dlg.doModal()


class dialogWait:
    # didn't work, xbmc crash when use it

    def __init__(self, header, info):
        xbmc.executebuiltin('Skin.SetString(waitheader,%s)' % header)
        xbmc.executebuiltin('Skin.SetString(waitinfo,%s)' % info)
        self.dlg = xbmcgui.WindowXMLDialog('DialogWait.xml', ROOTDIR)

    def show(self):
        self.dlg.show()

    def close(self):
        self.dlg.close()

BACKGROUND = 0
FOREGROUND = 1


class dialogWaitBackground:
    LINEGUICONTROL = [45001, 45002, 45003, 45004, 45005]
    BUTTONCONTROL = 10

    def __init__(self, header, lines=[], checkFn=None, logfile=None,
                 polltime=2000, skinvar=None, id=False, onFinishedCB=None):
        self.header = header
        self.lines = collections.deque(maxlen=len(self.LINEGUICONTROL))
        self.lines.extend(lines)
        self.checkFn = checkFn
        self.polltime = polltime
        self.logFile = logfile
        self.skinvar = skinvar
        self.id = id
        self.onFinishedCB = onFinishedCB
        self.state = FOREGROUND
        self.dlgForeground = xbmcgui.WindowXMLDialog('DialogWaitBackground.xml', ROOTDIR)
        self.finished = False
        xbmc.executebuiltin('Skin.SetString(backgrounddialogheader,%s)' % self.header)

    def show(self):
        # display foreground dialog
        if self.skinvar:
            setvisiblecondition(self.skinvar, True)
        if self.logFile:
            try:
                i = 0
                while i < 5:
                    if os.path.isfile(self.logFile):
                        break
                    xbmc.sleep(500) # Give background job a bit time to create logfile
                    i = i + 1
                self.logFile = open(self.logFile, 'r')
            except:
                print 'Cant open logfile %s' % (self.logFile,)
                self.logFile = None

        self.backgroundThread = threading.Thread(None, self._pollLoop, None)
        self.backgroundThread.start()
        self.dlgForeground.doModal()
        if not self.finished:
            self.onBackground()

    def lineProgress(self, lineNb, message):
        self.lines[lineNb] = message
        self._updateGui()

    def circularProgress(self, message):
        self.lines.append(message)
        self._updateGui()

    def _updateGui(self):
        for i, line in enumerate(self.lines):
            # print 'set label %s to %s'%(str(self.guiLineControl[i]),line)
            self.guiLineControl[i].setLabel(line)

    def close(self):
        if self.state == FOREGROUND:
            self.dlgForeground.getControl(self.BUTTONCONTROL).setLabel('Close')
        if self.logFile:
            self.logFile.close()
            self.logFile = None

    def onBackground(self):
        self.state == BACKGROUND
        self.close()

    def onFinished(self):
        if self.onFinishedCB:
            self.onFinishedCB()
        if self.skinvar:
            setvisiblecondition(self.skinvar, False)
        self.finished = True
        self.close()

    def _checkNewLog(self):
        # check if new log(s) in file
        while self.logFile:
            try:
                line = self.logFile.readline().strip()
            except:
                print 'Cant read logfile'
                line = None
            if not line:
                break
            else:
                self.circularProgress(line)

    def _pollLoop(self):
        xbmc.sleep(1000)
        self.guiLineControl = []
        for control in self.LINEGUICONTROL:
            self.guiLineControl.append(self.dlgForeground.getControl(control))
        self._updateGui()
        if self.checkFn:
            while not self.checkFn():
                self._poll()
            self._poll()
            self.onFinished()

    def _poll(self):
        # poll log file every second
        for i in xrange(0, self.polltime, 1000):
            if self.logFile and self.state == FOREGROUND:
                self._checkNewLog()
            xbmc.sleep(1000)
        if i < self.polltime:
            if self.logFile and self.state == FOREGROUND:
                self._checkNewLog()
            xbmc.sleep(self.polltime - i)


SSID = 0
SECURITYTYPE = 1
SECURITY = 2
SIGNAL = 3


def wifiConnect(interface):
    dialog = xbmcgui.Dialog()
    progress = dialogWait(_('Scan'), _('Scanning for available networks...'))
    progress.show()
    networklist = xbianConfig('network', 'scan', interface)
    networks = []
    for network in networklist:
        tmp = network.split(',')
        tmp[SSID] = tmp[SSID].replace('"', '')
        networks.append(tmp)
    progress.close()
    canceled = False

    while not canceled:
        displaylist = []
        for network in networks:
            signalI = int(network[SIGNAL])
            if 0 <= signalI < 20:
                signal = '[[COLOR red]*[/COLOR]****]'
            elif 20 <= signalI < 40:
                signal = '[[COLOR orange]**[/COLOR]***]'
            elif 40 <= signalI < 60:
                signal = '[[COLOR orange]***[/COLOR]**]'
            elif 60 <= signalI < 80:
                signal = '[[COLOR green]****[/COLOR]*]'
            else:
                signal = '[[COLOR green]*****[/COLOR]]'

            name = '%s %s' % (signal, network[SSID])
            displaylist.append(name)
        selectedNetwork = dialog.select(_('SSID'), displaylist)
        if selectedNetwork == -1:
            canceled = True
        else:
            if networks[selectedNetwork][SECURITY] == 'on':
                rc = xbianConfig('network', 'credentials', interface, networks[selectedNetwork][SECURITYTYPE], base64.b64encode(networks[selectedNetwork][SSID]))
                if rc:
                    key = base64.b64decode(rc[0])[:-1]
                else:
                    key = ''
                key = getText('%s: %s (%s)' % (_('Enter credentials for selected interface'), networks[selectedNetwork][SSID], networks[selectedNetwork][SECURITYTYPE]), key)
                if not key:
                    continue
            else:
                key = ""
            progress = dialogWait(
                interface,
                _('Please wait. Trying to connect to %s') % (
                    networks[selectedNetwork][SSID], ))
            progress.show()
            retry = 2
            current_try = 1
            connected = False
            while not connected and current_try <= retry:
                rc = xbianConfig('network', 'credentials', interface, networks[selectedNetwork][
                                 SECURITYTYPE], base64.b64encode(networks[selectedNetwork][SSID]), base64.b64encode(key))
                if rc and rc[0] == '1':
                    restart = xbianConfig('network', 'restart', interface)
                    if restart and restart[0] == '1':
                        rc = '2'
                        lc = 0
                        while (rc == '2' or rc == '-12') and lc < 60:
                            tmp = xbianConfig('network', 'progress', interface)
                            if tmp:
                                rc = tmp[0]
                            time.sleep(1)
                            lc += 1
                        if rc == '1':
                            progress.close()
                            return True
                        else:
                            current_try += 1
                    else:
                        progress.close()
                        # dialog.ok("Wireless Error",'Cannot restart %s'%interface)
                        return False
                else:
                    progress.close()
                    dialog.ok(interface, _('Failed to connect to %s') % (
                        networks[selectedNetwork][SSID], rc, ))
                    return False
    return False


def visiblecondition(key):
    return 'StringCompare(Window.Property(%s),1)' % key


def setvisiblecondition(key, value, id=False):
    if id:
        xbmc.executebuiltin('SetProperty(%s,%d,%d)' % ( key, 1 if value else 0, id))
    else:
        xbmc.executebuiltin('SetProperty(%s,%d,%d)' % ( key, 1 if value else 0, xbmcgui.getCurrentWindowId()))
    xbmc.executebuiltin('SetProperty(%s,%d)' % ( key, 1 if value else 0))


ADVANCED = Tag('visible', visiblecondition('advancedmode'))
