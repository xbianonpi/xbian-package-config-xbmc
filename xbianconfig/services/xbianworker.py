from __future__ import print_function

import os
import xbmc
import xbmcgui
from xbmcaddon import Addon
from resources.lib.service import service
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
from datetime import datetime, timedelta

import resources.lib.translation
_ = resources.lib.translation.language.gettext

__addonID__ = "plugin.xbianconfig"
ADDON = Addon(__addonID__)

#
# Predefined messages for external programs
#
msgs = [
  [ _('Update notification'), '', _('Resident part of package xbmc-config has been changed'), _('A restart of Kodi is recommended') ],
  [ _('Update notification'), '', _('Package xbmc has been updated'), _('You have to restart Kodi immediately') ],
  [ _('Update notification'), '', _('Package upstart-xbmc-bridge has been updated'), _('A restart of Kodi is recommended') ],
  [  '4.1',  '4.2',  '4.3' ],
  [  '5.1',  '5.2',  '5.3' ],
  [  '6.1',  '6.2',  '6.3' ],
  [  '7.1',  '7.2',  '7.3' ],
  [  '8.1',  '8.2',  '8.3' ],
  [  '9.1',  '9.2',  '9.3' ],
  [ _('Security warning'),    '', _('The standard password of user xbian has not been changed yet'), _('Setting a new one is strongly recommended') ],
]

class xbianworker(service):

    def onInit(self):
        self.StopRequested = False
        self.updatesAvailable = False
        self.rebootPending = False
        self.upgradePending = False
        self.inScreenSaver = False
        self.forceRefresh = False
        self.hideUpdatesAvailable = False
        self.hideImageWarning = False
        self.hideHomeWarning = False
        self.hideUpgradeNotify = False
        self.settingsUpdated = False
        self.notifyWhenBusy = False
        self.refreshNext = datetime.now() + timedelta(minutes=30)
        self.xbiancopyDone = self.backuphomeDone = False
        self.xbiancopyDate = self.backuphomeDate = None
        self.timeImageDiff = self.timeHomeDiff = timedelta(minutes=30)
        self.msgdisp = 0
        self.msgcount = 10
        self.msgheader = []
        self.msgcontent = []
        self.loop = 600

        if int(getSetting('hide.updates')) == 1:
            self.hideUpdatesAvailable = True
        if int(getSetting('hide.xbiancopy')) == 1:
            self.hideImageWarning = True
        if int(getSetting('hide.backuphome')) == 1:
            self.hideHomeWarning = True
        if int(getSetting('hide.upgradenotify')) == 1:
            self.hideUpgradeNotify = True

        self.actualizeSettings()

        while self.msgcount > 0:
            self.msgheader.append('')
            self.msgcontent.append([ '', '', '' ])
            self.msgcount -= 1

        print('XBian-config : xbianworker service started')

    def actualizeSettings(self, notify=False):
        rc = xbianConfig('updates', 'enableauto')
        if rc and rc[0] == '1':
            self.enableauto = True
        else:
            self.enableauto = False

        try:
            rc = xbianConfig('updates', 'autoinventory')
            self.deltaCheck = int(rc[0].split(' ')[1])
            if rc[0].split(' ')[0] == '0':
                self.selfCheck = True
            else:
                self.selfCheck = False

        except:
            self.deltaCheck = 1
            self.selfCheck = True

        self.timeImageDiff = self.calcTimedelta('imgplan', self.xbiancopyDone)
        self.timeHomeDiff = self.calcTimedelta('homeplan', self.backuphomeDone)

        if int(getSetting('notifywhenbusy')) == 1:
            self.notifyWhenBusy = True
        else:
            self.notifyWhenBusy = False

        if notify:
            self.settingsUpdated = True
            self.loop = 10

    def calcTimedelta(self, type, done):
        if done:
            delta = timedelta(days=31,hours=3)
        else:
            delta = timedelta(days=21)
        planned = xbianConfig('xbiancopy', type)
        if planned:
            if planned[0] == 'daily':
                delta = timedelta(hours=27)
            elif planned[0] == 'weekly':
                delta = timedelta(days=7,hours=3)
            elif planned[0] == 'monthly':
                delta = timedelta(days=31,hours=3)
        return delta

    def onAbortRequested(self):
        print('XBian-config : abort requested')

        self.StopRequested = True
        try:
            os.system('/usr/bin/sudo /bin/kill $(cat /run/lock/xbian-config) >/dev/null 2>&1 || :')
        except:
            pass

    def doRefresh(self, force=False):
        print('XBian-config : on refresh (%s)' % ('Forced' if force else 'on saver'))
        self.refreshNext = self.eventTime + timedelta(hours=3)
        if not self.forceRefresh and (self.enableauto or self.StopRequested):
            return

        try:
            lucTime = getSetting('lastupdatecheck')
            if int(lucTime) == 0:
                lucTime = datetime.strptime('2012-01-01 0:00:00', '%Y-%m-%d %H:%M:%S')
        except:
            pass

        if self.forceRefresh or ((force or not xbmc.Player().isPlaying()) and self.selfCheck and (lucTime < (self.eventTime - timedelta(days=self.deltaCheck)))):

            setSetting('lastupdatecheck', self.eventTime)
            print('XBian-config : running internal database updates (%s)' % self.forceRefresh)

            # flush package cache if needed and refresh
            pkglist = xbianConfig('packages', 'list', cache=True)
            pkglistnc = xbianConfig('packages', 'list')
            if pkglistnc[0] == '-3' or str(pkglist) != str(pkglistnc):
                print('XBian-config : cleaning package cache')
                pkglist = xbianConfig('packages', 'updatedb', forceclean=True)
                if pkglist and pkglist[0] == '1':
                    pkglist = xbianConfig('packages', 'list', forcerefresh=True)
                    self.forceRefresh = False
            else:
                self.forceRefresh = False

            if pkglist and pkglist[0] != '-3':
                for pkg in pkglist:
                    xbianConfig('packages', 'list', pkg.split(',')[0], forcerefresh=True)

            # check if new upgrades avalaible
            rc = xbianConfig('updates', 'list', 'packages', forcerefresh=True)
            if rc and rc[0] == '-3':
                rc = xbianConfig('updates', 'updatedb')
                if rc and rc[0] == '1':
                    rc = xbianConfig('updates', 'list', 'packages', forcerefresh=True)

            if rc and rc[0] and len(rc[0]) > 2:
                self.updatesAvailable = True
                print('XBian-config : new updates available')
            else:
                self.updatesAvailable = False
                if int(getSetting('hide.updates')) != 1:
                    self.hideUpdatesAvailable = False
        print('XBian-config : on refresh done')


    def onScreensaverActivated(self):
        print('XBian-config : on saver')
        self.inScreenSaver = True
        self.eventTime = datetime.now()
        self.doRefresh()

    def onScreensaverDeactivated(self):
        print('XBian-config : on saver deactivated')
        self.inScreenSaver = False
        self.loop = 30

    def showRebootDialog(self):
        print('XBian-config : show reboot dialog')
        if xbmcgui.Dialog().yesno(
                'XBian-config',
                _('A reboot is required. Do you want to reboot now?')):
            xbmc.executebuiltin("Restart()")
        self.rebootPending = False

    def showHint(self, header, message, hint):
        print('XBian-config : show hint (%s)' % hint)
        if int(getSetting('advancedmode')) == 1:
            if xbmcgui.Dialog().yesno(
                    header,
                    message,'',
                    _('Never show this hint again?')):
                setSetting(hint, True)
        else:
            xbmcgui.Dialog().ok(header, message)
        return True

    def showMessage(self, header, messages):
        print('XBian-config : show message (%s)' % messages)
        xbmcgui.Dialog().ok(header, messages[0] + '\n' +  messages[1] + '\n' +  messages[2])
        return True

    def onIdle(self):
        self.eventTime = datetime.now()

        # for those one who deactivate its screensaver, force check for refresh every 3 hours
        if self.forceRefresh or self.refreshNext < self.eventTime:
            self.doRefresh(True)
            return

        if self.settingsUpdated:
            xbmc.executebuiltin('Notification(' + _('Service') + ' XBianWorker' + ', ' + _('%s successfully updated') % (_('Service'),) +')')
            self.settingsUpdated = False

        if self.inScreenSaver or self.StopRequested or (not self.notifyWhenBusy and xbmc.Player().isPlaying()):
            return

        if self.msgcount > 0:
            self.showMessage(self.msgheader[self.msgdisp], self.msgcontent[self.msgdisp])
            self.msgdisp += 1
            if self.msgdisp < self.msgcount:
                self.loop = 10
            else:
                self.msgcount = 0
                self.msgdisp = 0
            return

        if os.path.isfile('/tmp/.xbian_config_python'):
            return

        if self.rebootPending:
            rebootneeded = xbianConfig('reboot')
            if rebootneeded and rebootneeded[0] == '1':
                stillrunning = xbianConfig('updates', 'progress')
                if stillrunning and stillrunning[0] == '0':
                    self.showRebootDialog()
                    return

        if not self.hideUpgradeNotify and self.upgradePending:
            rc = xbianConfig('updates', 'distupgrade', 'query')
            if rc and rc[0] != '0':
                self.hideUpgradeNotify = self.showHint( _('Update') + ': ' + _('Distribution'), _('A distribution upgrade to %s is available') % (rc[0]), 'hide.upgradenotify')
            else:
                self.hideUpgradeNotify = False
            self.upgradePending = False
            return

        if not self.hideUpdatesAvailable and self.updatesAvailable:
            self.hideUpdatesAvailable = self.showHint( _('Package') + ' ' + _('Update'), _('Some XBian package can be updated'), 'hide.updates')
            self.updatesAvailable = False
            return

        if self.xbiancopyDate is not None:
            if not self.hideImageWarning and self.xbiancopyDate < (self.eventTime - self.timeImageDiff):
                self.hideImageWarning = self.showHint(_('System backup'), _('This type of backup has not been made for a long time!'), 'hide.xbiancopy')
                return

        if self.backuphomeDate is not None and self.xbiancopyDate is not None:
            if not self.hideHomeWarning and self.backuphomeDate < (self.eventTime - self.timeHomeDiff) and self.xbiancopyDate < (self.eventTime - self.timeImageDiff):
                self.hideHomeWarning = self.showHint(_('Home backup'), _('This type of backup has not been made for a long time!'), 'hide.backuphome')
                return

    def onStatusChanged(self, status, file=None):
        print('XBian-config : on status changed (%s,%s)' % (status,file))
        if status == 'setting':
            self.actualizeSettings(True)
        elif status == 'reboot':
            self.rebootPending = True
        elif status == 'upgrade':
            self.upgradePending = True
        elif status == 'noreboot':
            self.rebootPending = False
        elif status == 'refresh':
            self.forceRefresh = True
        elif status == 'msg4kodi':
            xbmc.sleep(500)
            fd = False
            try:
                fd = open(file, "r")
                i = 0
                self.msgheader[self.msgcount] = ''
                for line in fd:
                    line = line.rstrip()
                    if line[0] == '#':
                        msgno = int(line[1:]) - 1
                        for msg in msgs[msgno]:
                            if len(msg) == 0:
                                msg = ' '
                            if i == 0:
                                self.msgheader[self.msgcount] = msg
                                self.msgcontent[self.msgcount] = [ '', '', '' ]
                            elif i < 4:
                                self.msgcontent[self.msgcount][i-1] = msg
                            i += 1
                        self.msgcount += 1
                        i = 0
                    else:
                        if len(line) == 0:
                            line = ' '
                        if i == 0:
                            self.msgheader[self.msgcount] = line
                            self.msgcontent[self.msgcount] = [ '', '', '' ]
                            i += 1
                        elif line == '$':
                            self.msgcount += 1
                        elif i < 4:
                            self.msgcontent[self.msgcount][i-1] = line
                            i += 1
                self.loop = 10
            except:
                print('XBian-config : error reading message(s) from %s' % (file))
            if fd:
                fd.close()
            try:
                os.remove(file)
            except:
                pass
        elif status == 'xbiancopy':
            self.xbiancopyDate = datetime.fromtimestamp(os.path.getmtime(file))
            if os.path.getsize(file) > 0:
                self.xbiancopyDone = True
            self.actualizeSettings()
            if int(getSetting('hide.' + status)) != 1:
               self.hideImageWarning = False
        elif status == 'backuphome':
            self.backuphomeDate = datetime.fromtimestamp(os.path.getmtime(file))
            if os.path.getsize(file) > 0:
                self.backuphomeDone = True
            self.actualizeSettings()
            if int(getSetting('hide.' + status)) != 1:
                self.hideHomeWarning = False
        elif status == 'hide.xbiancopy':
            if int(getSetting(status)) == 1:
                self.hideImageWarning = True
            else:
                self.hideImageWarning = False
        elif status == 'hide.backuphome':
            if int(getSetting(status)) == 1:
                self.hideHomeWarning = True
            else:
                self.hideHomeWarning = False
        elif status == 'hide.upgradenotify':
            if int(getSetting(status)) == 1:
                self.hideUpgradeNotify = True
            else:
                self.hideUpgradeNotify = False
        elif status == 'hide.updates':
            if int(getSetting(status)) == 1:
                self.hideUpdatesAvailable = True
            else:
                self.hideUpdatesAvailable = False
                rc = xbianConfig('updates', 'list', 'packages')
                if rc and rc[0] and len(rc[0]) > 2:
                    self.updatesAvailable = True

    def onStart(self):
        # check is packages is updating
        if os.path.isfile('/var/lock/.packages'):
            if xbianConfig('updates', 'progress')[0] == '1':
                dlg = dialogWait('XBian' + ' ' +_('Update'), _('Please wait while updating'))
                dlg.show()
                while not self.StopRequested and xbianConfig('updates', 'progress')[0] == '1':
                    xbmc.sleep(300)
                dlg.close()
                if self.StopRequested:
                    return
            xbmc.executebuiltin("Notification(%s, %s)" % (_('Package') + ' ' + _('Update'), _('Updates installed successfully')))
            os.remove('/var/lock/.packages')

        if xbianConfig('updates', 'progress')[0] != '1':
            setvisiblecondition('aptrunning', False)

        while not self.StopRequested:  # End if XBMC closes
            self.onIdle()
            if self.loop == 0:
                self.loop = 600
            while not self.StopRequested and self.loop > 0:
                xbmc.sleep(500)  # Repeat (ms)
                self.loop = self.loop - 1

        xbianConfig() # Relese resources
        print('XBian-config : xbianworker service finished')
