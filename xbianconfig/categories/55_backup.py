from __future__ import print_function
from builtins import map

try:
    import itertools.ifilter as filter
except ImportError:
    pass

import datetime
import os
import threading

import xbmc
import xbmcgui

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category, Setting
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
import resources.lib.translation

_ = resources.lib.translation.language.gettext

BACKUP_PROFILE = ['daily', 'weekly', 'monthly']

DEVICE = 'Device'
FILE = 'File'

DESTINATION_HOME_RESTORE = '/xbmc-backup/put_here_to_restore/'
SYSTEMLOGFILE = '/tmp/xbiancopy.log'

class separator(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Manage snapshot')))


class homeBackupLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Home backup')))


class systemBackupLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('System backup')), ADVANCED)


class snapshotLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Auto snapshot')), ADVANCED)


class autodailysnapshot(MultiSettingControl):
    LABEL = _('Enable daily snapshot')

    def onInit(self):
        self.autodaily = RadioButtonControl(Tag('label', self.LABEL))
        self.addControl(self.autodaily)
        self.multiDelta = MultiSettingControl(
            Tag('visible', 'SubString(Control.GetLabel(%d),*)' % self.autodaily.getId()))
        self.countdaily = ButtonControl(
            Tag('label', '     -%s' % (_('Number of snapshot to keep'), )))
        self.countdaily.onClick = lambda count: self.countdaily.setValue(
            getNumeric(_('Number of snapshot to keep'), self.countdaily.getValue(), 1, 1000))
        self.multiDelta.addControl(self.countdaily)
        self.addControl(self.multiDelta)

    def getValue(self):
        return [self.autodaily.getValue(), int(self.countdaily.getValue())]

    def setValue(self, value):
        self.autodaily.setValue(value[0])
        self.countdaily.setValue(value[1])


class autoweeklysnapshot(autodailysnapshot):
    LABEL = _('Enable weekly snapshot')


class automonthlysnapshot(autodailysnapshot):
    LABEL = _('Enable monthly snapshot')


class systemSettingControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.systemAutoBackup = RadioButtonControl(
            Tag('label', _('Auto image')))
        self.addControl(self.systemAutoBackup)
        self.multiDelta = MultiSettingControl(
            Tag('visible', 'SubString(Control.GetLabel(%d),*)' % self.systemAutoBackup.getId()))
        self.systemdeltaControl = SpinControlex(
            Tag('label', ' -%s' % (_('Type'), )))
        for number in BACKUP_PROFILE:
            self.systemdeltaControl.addContent(Content(Tag('label', number), defaultSKin=False))
        self.multiDelta.addControl(self.systemdeltaControl)
        self.addControl(self.multiDelta)
        # Destination type (DEV/FILE) :
        self.systemBackupDestType = SpinControlex(
            Tag('label', _('Destination type')))
        self.addControl(self.systemBackupDestType)
        contentSD = Content(Tag('label', DEVICE), defaultSKin=False)
        self.systemBackupDestType.addContent(contentSD)
        contentSF = Content(Tag('label', FILE), defaultSKin=False)
        self.systemBackupDestType.addContent(contentSF)
        self.systemdevicePath = ButtonControl(
            Tag('label', ' -%s' % (_('Block device'), )),
            Tag('visible', 'StringCompare(Skin.String(%s),%s)' % (
                self.systemBackupDestType.getKey(), DEVICE)))
        self.systemdevicePath.onClick = lambda devicePath: self.systemdevicePath.setValue(
            self.getDevice())
        self.addControl(self.systemdevicePath)
        self.systemfilePath = ButtonControl(
            Tag('label', ' -%s' % (_('Destination: '), )),
            Tag('visible', 'StringCompare(Skin.String(%s),%s)' % (
                self.systemBackupDestType.getKey(), FILE)))
        self.systemfilePath.onClick = lambda backupPath: self.systemfilePath.setValue(getFile('Backup Path', self.systemfilePath.getValue(
        )) + getText('FileName', '$(hostname)_xbian_image_$(date +%F).img'))
        self.addControl(self.systemfilePath)
        self.systemKeep = ButtonControl(
            Tag('label', ' -%s' % (_('Number of images to keep'), )),
            Tag('visible', 'StringCompare(Skin.String(%s),%s)' % (self.systemBackupDestType.getKey(), FILE)))
        self.systemKeep.onClick = lambda count: self.systemKeep.setValue(
            getNumeric(_('Number of images to keep'), self.systemKeep.getValue(), 0))
        self.addControl(self.systemKeep)

    def getDevice(self):
        # to be override in gui - CB to display select dialog for ?UUID?
        pass

    def startManualBackup(self):
        # to be override in gui - CB to startManualBackup
        pass

    def setValue(self, value):
        print('systemSettingControl setValue', value)
        # by default, display system auto backup
        #
        # value = [
        #  1,                   # system backup enable
        #  'Device'/'File',     # system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', # system Path
        #  BACKUP_PROFILE[x],   # system backup delta
        #  n                    # system number of images to keep
        #
        # ]
        self.systemAutoBackup.setValue(value[0])
        self.systemBackupDestType.setValue(value[1])
        if value[1] == DEVICE:
            self.systemdevicePath.setValue(value[2])
        else:
            self.systemfilePath.setValue(value[2])
        self.systemdeltaControl.setValue(value[3])
        self.systemKeep.setValue(value[4])

    def getValue(self):
        value = []
        value.append(self.systemAutoBackup.getValue())
        value.append(self.systemBackupDestType.getValue())
        if value[-1] == DEVICE:
            value.append(self.systemdevicePath.getValue())
        else:
            value.append(self.systemfilePath.getValue())
        value.append(self.systemdeltaControl.getValue())
        value.append(self.systemKeep.getValue())
        return value


class systemSettingGui(Setting):
    CONTROL = systemSettingControl(ADVANCED)
    DIALOGHEADER = _('System backup')

    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self):
        # override CB
        self.control.getDevice = self.getDevice
        self.rc = 0

    def getDevice(self):
        dialog = xbmcgui.Dialog()
        # get a list of uuid here (maybe with size to prevent error)
        # Need a protection to not erase usb HDD with media?
        uuid_list = xbianConfig('xbiancopy', 'getpart', 'all')
        #uuid_list = [x for x in uuid_list[0].split(';') if len(x) > 0]
        uuid_list = list(filter(lambda x: len(x) > 0, uuid_list[0].split(';')))
        rc = dialog.select(_('Select Device'), uuid_list)
        if rc == -1:
            return self.xbianValue[2]  # defaut device value in case of cancel
        else:
            return uuid_list[rc]

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        # value = [
        #  1/0,                 # auto backup enable
        #  'Device'/'File',     # system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', # system Path
        #  BACKUP_PROFILE[x],   # system backup delta
        #  n                    # system number of images to keep
        # ]
        if xbianConfig('xbiancopy', 'imgtype')[0] == 'file':
            imgtype = 'File'
        else:
            imgtype = 'Device'
        delta = xbianConfig('xbiancopy', 'imgplan')
        if delta and delta[0] in BACKUP_PROFILE:
            delta = delta[0]
            actif = 1
        else:
            delta = BACKUP_PROFILE[0]
            actif = 0
        dest = xbianConfig('xbiancopy', 'imgdest')
        if dest:
            dest = dest[0]
        else:
            dest = ''
        num = xbianConfig('xbiancopy', 'imgkeep')
        if num:
            num = num[0]
        else:
            num = 0
        return [actif, imgtype, dest, delta, num]

    def setXbianValue(self, value):
        # value is like [1,'File','/home/belese/', 'Daily', 3]
        # or [1,'Device','UUID','Daily']
        if value[1] == 'File':
            value[1] = 'file'
        if value[1] == 'Device':
            value[1] = 'block'
        if value[0] == 0:
            value[3] = 'none'
        if xbianConfig('xbiancopy', 'imgplan', value[3])[0] != '1':
            return False
        if xbianConfig('xbiancopy', 'imgtype', value[1])[0] != '1':
            return False
        if xbianConfig('xbiancopy', 'imgdest', value[2])[0] != '1':
            return False
        if xbianConfig('xbiancopy', 'imgkeep', value[4])[0] != '1':
            return False
        return True


class systemExecControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.systemAutoBackup = RadioButtonControl(Tag('visible', 'FALSE'))
        self.systemdeltaControl = SpinControlex(Tag('visible', 'FASLE'))
        self.systemBackupDestType = SpinControlex(Tag('visible', 'FASLE'))
        self.systemdevicePath = ButtonControl(Tag('visible', 'FALSE'))
        self.systemfilePath = ButtonControl(Tag('visible', 'FALSE'))
        self.systemKeep = ButtonControl(Tag('visible', 'FALSE'))

        self.ManualBackup = ButtonControl(
            Tag('label', _('Start backup now')),
            Tag('visible', '!%s' % (visiblecondition('backuprunning'), )))
        self.ManualBackup.onClick = lambda manualback: self.startManualBackup()
        self.addControl(self.ManualBackup)

    def getDevice(self):
        # to be override in gui - CB to display select dialog for ?UUID?
        pass

    def startManualBackup(self):
        # to be override in gui - CB to startManualBackup
        pass

    def setValue(self, value):
        print('systemExecControl setValue', value)
        # by default, display system auto backup
        #
        # value = [
        #  1,                   # system backup enable
        #  'Device'/'File',     # system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', # system Path
        #  BACKUP_PROFILE[x],   # system backup delta
        #  n                    # system number of images to keep
        #
        # ]
        self.systemAutoBackup.setValue(value[0])
        self.systemBackupDestType.setValue(value[1])
        if value[1] == DEVICE:
            self.systemdevicePath.setValue(value[2])
        else:
            self.systemfilePath.setValue(value[2])
        self.systemdeltaControl.setValue(value[3])
        self.systemKeep.setValue(value[4])

    def getValue(self):
        value = []
        value.append(self.systemAutoBackup.getValue())
        value.append(self.systemBackupDestType.getValue())
        if value[-1] == DEVICE:
            value.append(self.systemdevicePath.getValue())
        else:
            value.append(self.systemfilePath.getValue())
        value.append(self.systemdeltaControl.getValue())
        value.append(self.systemKeep.getValue())
        return value


class systemExecGui(Setting):
    CONTROL = systemExecControl(ADVANCED)
    DIALOGHEADER = _('System backup')

    def onInit(self):
        # override CB
        self.control.getDevice = self.getDevice
        self.control.startManualBackup = self.startManualBackup
        self.rc = 0

    def checkcopyFinish(self):
        self.rc = xbianConfig('xbiancopy', 'status')[0]
        return self.rc != '0'

    def oncopyFinished(self):
        if self.rc == '1':
            # backup is finished
            self.OKTEXT = _('Backup system is finished')
            if self.value[1] == 'File':
                xbianConfig('xbiancopy', 'doclean', self.value[2], self.keep)
            self.notifyOnSuccess()
        else:
            if self.rc == '-1':
                self.ERRORTEXT = _("Can't prepare destination filesystem")
            elif self.rc == '-2':
                # shouldn't see this error
                self.ERRORTEXT = _('Backup not started')
            else:
                self.ERRORTEXT = _('An unexpected error occurred')
            self.notifyOnError()

    def startManualBackup(self):
        #self.value = self.control.getValue()
        self.value = self.getXbianValue()
        AT = self.APPLYTEXT
        if self.value[1] == 'File':
            self.value[2] = 'file:' + self.value[2]
            dest = xbianConfig('xbiancopy', 'imgdest', 'exp')[0]
            self.APPLYTEXT = _('Write backup to %s?') % ('...' + dest[len(dest)-57:] if len(dest) > 60 else dest, )
            confirm = False
            self.keep = self.value[4]
        else:
            self.APPLYTEXT = _('This will erase ALL data on %s, continue?') % (
                self.value[2], )
            confirm = True
            self.keep = 0

        if self.askConfirmation(confirm):
            xbianConfig('xbiancopy', 'start', '/dev/root', self.value[2])
            dlg = dialogWaitBackground(
                _('XBian System Backup'), [_('Please wait while creating backup file')],
                self.checkcopyFinish,
                SYSTEMLOGFILE,
                skinvar='backuprunning',
                id=xbmcgui.getCurrentWindowId(),
                onFinishedCB=self.oncopyFinished)
            dlg.show()
        self.APPLYTEXT = AT
        return ''

    def getDevice(self):
        dialog = xbmcgui.Dialog()
        # get a list of uuid here (maybe with size to prevent error)
        # Need a protection to not erase usb HDD with media?
        uuid_list = xbianConfig('xbiancopy', 'getpart')
        #uuid_list = [x for x in uuid_list[0].split(';') if len(x) > 0]
        uuid_list = list(filter(lambda x: len(x) > 0, uuid_list[0].split(';')))
        rc = dialog.select(_('Select Device'), uuid_list)
        if rc == -1:
            return self.xbianValue[2]  # defaut device value in case of cancel
        else:
            return uuid_list[rc]

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        # value = [
        #  1/0,                 # auto backup enable
        #  'Device'/'File',     # system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', # system Path
        #  BACKUP_PROFILE[x],   # system backup delta
        #  n                    # system number of images to keep
        # ]
        if xbianConfig('xbiancopy', 'imgtype')[0] == 'file':
            imgtype = 'File'
        else:
            imgtype = 'Device'
        delta = xbianConfig('xbiancopy', 'imgplan')
        if delta and delta[0] in BACKUP_PROFILE:
            delta = delta[0]
            actif = 1
        else:
            delta = BACKUP_PROFILE[0]
            actif = 0
        dest = xbianConfig('xbiancopy', 'imgdest')
        if dest:
            dest = dest[0]
        else:
            dest = ''
        num = xbianConfig('xbiancopy', 'imgkeep')
        if num:
            num = num[0]
        else:
            num = 0
        return [actif, imgtype, dest, delta, num]

    def setXbianValue(self, value):
        print('In systemExecGui setXbianValue was called, please FIXME')
        return True


class homeSettingControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.homeAutoBackup = RadioButtonControl(Tag('label', _('Auto image')))
        self.addControl(self.homeAutoBackup)

        self.multiDelta = MultiSettingControl(Tag('visible', 'SubString(Control.GetLabel(%d),*)' % self.homeAutoBackup.getId()))
        self.homedeltaControl = SpinControlex(Tag('label', ' -%s' % (_('Type'), )))
        for number in BACKUP_PROFILE:
            self.homedeltaControl.addContent(Content(Tag('label', number), defaultSKin=False))
        self.multiDelta.addControl(self.homedeltaControl)
        self.addControl(self.multiDelta)

        self.homefilePath = ButtonControl(
            Tag('label', ' -%s' % (_('Destination: '), )),
            Tag('visible', 'SubString(Control.GetLabel(%d),*)' % self.homeAutoBackup.getId()))
        self.homefilePath.onClick = lambda backupPath: self.homefilePath.setValue(getFile('Backup Path', self.homefilePath.getValue(
        )) + getText('FileName', '$(hostname)_backup_home_$(date +%F).img.gz'))
        self.addControl(self.homefilePath)

        self.homeKeep = ButtonControl(
            Tag('label', ' -%s' % (_('Number of images to keep'), )),
            Tag('visible', 'SubString(Control.GetLabel(%d),*)' % self.homeAutoBackup.getId()))
        self.homeKeep.onClick = lambda count: self.homeKeep.setValue(
            getNumeric(_('Number of images to keep'), self.homeKeep.getValue(), 0))
        self.addControl(self.homeKeep)

    def setValue(self, value):
        print('homeSettingControl setValue', value)
        # by default, display home auto backup
        #
        # value = [
        #  1,                   # /home backup enable
        #  'backup_filepath',   # /home file incl. path
        #  BACKUP_PROFILE[x],   # /home backup delta
        #  n                    # /home number of images to keep
        # ]
        self.homeAutoBackup.setValue(value[0])
        self.homefilePath.setValue(value[1])
        self.homedeltaControl.setValue(value[2])
        self.homeKeep.setValue(value[3])

    def getValue(self):
        value = []
        value.append(self.homeAutoBackup.getValue())
        value.append(self.homefilePath.getValue())
        value.append(self.homedeltaControl.getValue())
        value.append(self.homeKeep.getValue())
        return value


class homeSettingGui(Setting):
    CONTROL = homeSettingControl(ADVANCED)
    DIALOGHEADER = _('Home backup')

    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        # value = [
        #  1/0,                 # /home backup enable
        #  'backup_filepath',   # /home file incl. path
        #  BACKUP_PROFILE[x]    # /home backup delta
        #  n                    # /home number of images to keep
        # ]
        delta = xbianConfig('xbiancopy', 'homeplan')
        if delta and delta[0] in BACKUP_PROFILE:
            delta = delta[0]
            actif = 1
        else:
            delta = BACKUP_PROFILE[0]
            actif = 0
        dest = xbianConfig('xbiancopy', 'homedest')
        if dest:
            dest = dest[0]
        else:
            dest = ''
        num = xbianConfig('xbiancopy', 'homekeep')
        if num:
            num = num[0]
        else:
            num = 0
        return [actif, dest, delta, num]

    def setXbianValue(self, value):
        # value is like [1,'/mnt/backup/$(hostname)_home_backup_$(date +%F).img.gz', 'Daily', 3]
        if value[0] == 0:
            value[2] = 'none'
        if xbianConfig('xbiancopy', 'homeplan', value[2])[0] != '1':
            return False
        if xbianConfig('xbiancopy', 'homedest', value[1])[0] != '1':
            return False
        if xbianConfig('xbiancopy', 'homekeep', str(value[3]))[0] != '1':
            return False
        return True


class homeExecControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.homeManualBackup = RadioButtonControl(Tag('visible', 'FALSE'))
        self.homedeltaControl = SpinControlex(Tag('visible', 'FALSE'))
        self.homefilePath = ButtonControl(Tag('visible', 'FALSE'))
        self.homeKeep = ButtonControl(Tag('visible', 'FALSE'))

        self.ManualBackup = ButtonControl(
            Tag('label', _('Start backup now')),
            Tag('visible', '!%s' % (visiblecondition('backuprunning'), )))
        self.ManualBackup.onClick = lambda manualback: self.startManualBackup()
        self.addControl(self.ManualBackup)
        self.ManualRestore = ButtonControl(
            Tag('label', _('Restore backup')),
            Tag('visible', '!%s' % (visiblecondition('backuprunning'), )))
        self.ManualRestore.onClick = lambda manualrestore: self.startManualRestore()
        self.addControl(self.ManualRestore)

    def startManualBackup(self):
        # to be override in ExecGui - CB to startManualBackup
        pass

    def startManualRestore(self):
        # to be override in ExecGui - CB to startManualRestore
        pass

    def setValue(self, value):
        print('homeExecControl setValue', value)
        # by default, display home auto backup
        #
        # value = [
        #  1,                   # /home backup enable
        #  'backup_filepath',   # /home file incl. path
        #  BACKUP_PROFILE[x],   # /home backup delta
        #  n                    # /home number of images to keep
        # ]
        self.homeManualBackup.setValue(value[0])
        self.homefilePath.setValue(value[1])
        self.homedeltaControl.setValue(value[2])
        self.homeKeep.setValue(value[3])

    def getValue(self):
        value = []
        value.append(self.homeManualBackup.getValue())
        value.append(self.homefilePath.getValue())
        value.append(self.homedeltaControl.getValue())
        value.append(self.homeKeep.getValue())
        return value


class homeExecGui(Setting):
    CONTROL = homeExecControl()
    DIALOGHEADER = _('Home backup')

    def onInit(self):
        # override CB
        self.control.startManualBackup = self.startManualBackup
        self.control.startManualRestore = self.startManualRestore
        self.rc = 0

    def checkcopyFinish(self):
        self.rc = xbianConfig('xbiancopy', 'homestatus')[0]
        return self.rc != '0'

    def oncopyFinished(self):
        if self.rc == '1':
            # backup is finished
            self.OKTEXT = _(
                "Backup /home is finished. In case of destination folder"
                "/xbmc-backup, please grab the file over network or save locally.")
            if self.keep > 0:
                xbianConfig('xbiancopy', 'doclean', self.value[1], self.keep)
            self.notifyOnSuccess()
        else:
            if self.rc == '-1':
                self.ERRORTEXT = _("Can't prepare destination filesystem")
            elif self.rc == '-2':
                # shouldn't see this error
                self.ERRORTEXT = _('Backup not started')
            else:
                self.ERRORTEXT = _('An unexpected error occurred')
            self.notifyOnError()

    def startManualBackup(self):
        #self.value = self.control.getValue()
        self.value = self.getXbianValue()
        if self.value[0] == 1 and getSetting('advancedmode') == '1':
            dest = xbianConfig('xbiancopy', 'homedest', 'exp')[0]
            self.keep = self.value[3]
        else:
            dest ='/xbmc-backup/%s_backup_home_%s.img.gz' % (os.uname()[1], datetime.datetime.now().strftime("%d-%m-%y"))
            self.keep = 0

        AT = self.APPLYTEXT
        self.APPLYTEXT = _('Write backup to %s?') % ('...' + dest[len(dest)-57:] if len(dest) > 60 else dest, )
        confirm = False
        if self.askConfirmation(confirm):
            xbianConfig('xbiancopy', 'homestart', dest)
            msg = [
                _('It can take several minutes depending on size of your /home directory'),
                _('If file is created under /xbian-backup, it is also accessible through smb share'),
                _('Until finished, there will be just temp folder. Once ready, .img.gz file will appear.'),
                _('You can copy the file directly to you computer (the file will be deleted during boot!)'),
                _('To restore your /home folder, just copy .img.gz file to /xbian-backup/put_to_restore folder.'),
            ]
            dlg = dialogWaitBackground(
                _('Backup /home to file'),
                msg,
                self.checkcopyFinish,
                skinvar='backuprunning',
                id=xbmcgui.getCurrentWindowId(),
                onFinishedCB=self.oncopyFinished)
            dlg.show()
        self.APPLYTEXT = AT
        return ''

    def checkcopyFinishRestore(self):
        return self.copyFileStatus != 0

    def oncopyFinishedRestore(self):
        if self.copyFileStatus == -1:
            self.notifyOnError()
            return
        ok = xbmcgui.Dialog().ok('Restore /home in progress', _('Please wait, /home is restored in background now'), _('After this has been done, Kodi will be restarted automatically'))

    def copyThread(self, src, dest):
        import xbmcvfs
        # copy is blocking, run in a thread for background dialog
        self.copyFileStatus = 0
        if xbmcvfs.copy(src, dest):
            self.copyFileStatus = 1
        else:
            self.copyFileStatus = -1

    def startManualRestore(self):
        src = xbmcgui.Dialog().browse(
            1, _('Select Home Image'), 'files', '.img.gz')
        AT = self.APPLYTEXT
        self.APPLYTEXT = _('Do you want to restore /home from %s') % (src, )
        if src and self.askConfirmation():
            # start thread copy
            copyT = threading.Thread(target=self.copyThread, args=(
                src, DESTINATION_HOME_RESTORE + '/xbianconfigrestore.img.gz'))
            copyT.start()
            msg = [_('It can take several minutes depending on size of '
                     'your backup image.')]
            dlg = dialogWaitBackground(
                _('Restore backup'),
                msg,
                self.checkcopyFinishRestore,
                skinvar='backuprunning',
                id=xbmcgui.getCurrentWindowId(),
                onFinishedCB=self.oncopyFinishedRestore)
            dlg.show()
        AT = self.APPLYTEXT
        return ''

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        # value = [
        #  1/0,                 # /home backup enable
        #  'backup_filepath',   # /home file incl. path
        #  BACKUP_PROFILE[x],   # /home backup delta
        #  n                    # /home number of images to keep
        # ]
        delta = xbianConfig('xbiancopy', 'homeplan')
        if delta and delta[0] in BACKUP_PROFILE:
            delta = delta[0]
            actif = 1
        else:
            delta = BACKUP_PROFILE[0]
            actif = 0
        dest = xbianConfig('xbiancopy', 'homedest')
        if dest:
            dest = dest[0]
        else:
            dest = ''
        num = xbianConfig('xbiancopy', 'homekeep')
        if num:
            num = num[0]
        else:
            num = 0
        return [actif, dest, delta, num]

    def setXbianValue(self, value):
        print('In homeExecGui setXbianValue was called, please FIXME')
        return True


class snapshotMount(Setting):
    CONTROL = ButtonControl(Tag('label', _('Mount a snapshot')), ADVANCED)
    DIALOGHEADER = _('Snapshot')
    PROGRESSTEXT = _('Please wait...')
    EXCLUDE = 'swap'

    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER, _('Loading volumes...'))
        load.show()
        volumeList = xbianConfig('listvol', '--exclude=%s' % self.EXCLUDE, cmd=['sudo', 'btrfs-auto-snapshot'])
        load.close()
        have_to_stop = False
        dialog = xbmcgui.Dialog()
        while not have_to_stop:
            volId = dialog.select(_('Btrfs volume'), volumeList)
            if volId == -1:
                have_to_stop = True
            else:
                load = dialogWait(self.DIALOGHEADER, _('Please wait...'))
                load.show()
                snapshotList = xbianConfig(
                    'list', volumeList[volId], cmd=['sudo', 'btrfs-auto-snapshot'])
                #snapshotList = [x for x in snapshotList if x.split('@')[1]]
                snapshotList = list(filter(lambda x: x.split('@')[1], snapshotList))
                load.close()
                #snapId = dialog.select('Snapshot', [x.split('@')[1] for x in snapshotList])
                snapId = dialog.select('Snapshot', list(map(lambda x: x.split('@')[1], snapshotList)))
                if snapId != -1 and self.askConfirmation():
                    try:
                        dlg = dialogWait(self.DIALOGHEADER, self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(volumeList[volId], snapshotList[snapId])
                    except:
                        print('error running btrfs-auto-spashot command %s %s' % (volumeList[volId], snapshotList[snapId]))
                    finally:
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self, volume, snapshot):
        xbianConfig('mount', '--helper', snapshot, cmd=['sudo', 'btrfs-auto-snapshot'])
        setvisiblecondition('umountsnapshot', xbianConfig('mount', cmd=['sudo', 'btrfs-auto-snapshot']))

    def getXbianValue(self):
        return ''


class snapshotUmount(Setting):
    CONTROL = ButtonControl(Tag('label', _('Umount a snapshot')), ADVANCED, Tag('visible', visiblecondition('umountsnapshot')))
    DIALOGHEADER = _('Snapshot')
    PROGRESSTEXT = _('Please wait...')
    EXCLUDE = 'swap'

    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER, _('Loading volumes...'))
        load.show()
        mountList = xbianConfig('mount', '--helper', cmd=['sudo', 'btrfs-auto-snapshot'])
        sep = xbianConfig('fstype', cmd=['sudo', 'btrfs-auto-snapshot'])[1]
        load.close()
        have_to_stop = False
        dialog = xbmcgui.Dialog()
        while not have_to_stop:
            #volId = dialog.select(_('Btrfs volume'), [x.split(sep)[0] for x in mountList])
            volId = dialog.select(_('Btrfs volume'), list(map(lambda x: x.split(sep)[0], mountList)))
            if volId == -1:
                have_to_stop = True
            else:
                #selectedVolume = [x.split(sep)[0] for x in mountList][volId]
                #mountItems = [x for x in mountList if selectedVolume + sep in x]
                #snapId = dialog.select('Snapshot', [x.split(sep)[1] for x in mountItems])
                selectedVolume = list(map(lambda x: x.split(sep)[0], mountList))[volId]
                mountItems = list(filter(lambda x: selectedVolume + sep in x, mountList))
                snapId = dialog.select('Snapshot', list(map(lambda x: x.split(sep)[1], mountItems)))
                if snapId != -1 and self.askConfirmation():
                    try:
                        dlg = dialogWait(self.DIALOGHEADER, self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(selectedVolume, mountItems[snapId])
                    except:
                        print('error running btrfs-auto-spashot command %s' % (mountItems[snapId]))
                    finally:
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self, volume, snapshot):
        xbianConfig('umount', '--helper', snapshot, cmd=['sudo', 'btrfs-auto-snapshot'])
        setvisiblecondition('umountsnapshot', xbianConfig('mount', cmd=['sudo', 'btrfs-auto-snapshot']))

    def getXbianValue(self):
        return ''


class snapshotRollback(snapshotMount):
    CONTROL = ButtonControl(Tag('label', _('Rollback to a snapshot')))
    PROGRESSTEXT = _('Please wait...')
    EXCLUDE = 'modules,swap'

    def runCmd(self, volume, snapshot):
        xbianConfig('rollback', snapshot, cmd=['sudo', 'btrfs-auto-snapshot'])
        dialog = xbmcgui.Dialog().yesno(
            'Reboot', _('A reboot is required. Do you want to reboot now?'))
        if dialog:
            xbmc.executebuiltin('Reboot')


class snapshotDestroy(snapshotMount):
    CONTROL = ButtonControl(Tag('label', _('Delete a snapshot')), ADVANCED)
    PROGRESSTEXT = _('Please wait...')

    def runCmd(self, volume, snapshot):
        xbianConfig('destroy', snapshot, cmd=['sudo', 'btrfs-auto-snapshot'])


class snapshotCreate(Setting):
    CONTROL = ButtonControl(Tag('label', _('Create a snapshot')))
    DIALOGHEADER = _('Snapshot')
    PROGRESSTEXT = _('Please wait...')
    EXCLUDE = 'swap'

    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER, _('Loading volumes...'))
        load.show()
        volumeList = xbianConfig('listvol', '--exclude=%s' % self.EXCLUDE, cmd=['sudo', 'btrfs-auto-snapshot'])
        try:
            self.fstype = xbianConfig('fstype', cmd=['sudo', 'btrfs-auto-snapshot'])[0] + '-'
        except:
            self.fstype=''
        load.close()
        have_to_stop = False
        dialog = xbmcgui.Dialog()
        while not have_to_stop:
            volId = dialog.select('Volume', volumeList)
            if volId == -1:
                have_to_stop = True
            else:
                snapshot = getText(
                    _('Snapshot name'),
                    '%suser-snap-%s' % (
                        self.fstype, datetime.datetime.now().strftime("%Y-%m-%d-%H%M"), ))
                if snapshot and self.askConfirmation():
                    try:
                        dlg = dialogWait(self.DIALOGHEADER, self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(volumeList[volId], snapshot)
                    except:
                        print('error running btrfs-auto-spashot command %s %s' % (volumeList[volId], snapshot))
                    finally:
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self, volume, snapshot):
        xbianConfig('snapshot', '--name', snapshot, volume, cmd=['sudo', 'btrfs-auto-snapshot'])

    def getXbianValue(self):
        return ''


class dailySnapshotGui(Setting):
    CONTROL = autodailysnapshot(ADVANCED)
    DIALOGHEADER = "Daily Snapshot"
    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self):
        self.key = 'dodaily'

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        rc = xbianConfig('xbiancopy', self.key)
        if rc:
            rc = rc[0].split(' ')
        if rc[0] == '0':
            rc.append(10)
        return list(map(int, rc))

    def setXbianValue(self, value):
        if value[0] == 1 or value[0] == 'True' or value[0] == True:
            value = value[1]
        else:
            value = 0
        rc = xbianConfig('xbiancopy', self.key, str(value))
        if rc and rc[0] == '0':
            return False
        else:
            return True


class weeklySnapshotGui(dailySnapshotGui):
    CONTROL = autoweeklysnapshot(ADVANCED)
    DIALOGHEADER = "Weekly Snapshot"

    def onInit(self):
        self.key = 'doweekly'


class monthlySnapshotGui(dailySnapshotGui):
    CONTROL = automonthlysnapshot(ADVANCED)
    DIALOGHEADER = "Monthly Snapshot"

    def onInit(self):
        self.key = 'domonthly'


class backup(Category):
    TITLE = _('Backup')
    SETTINGS = [homeBackupLabel, homeSettingGui, homeExecGui,
                systemBackupLabel, systemSettingGui, systemExecGui,
                snapshotLabel, dailySnapshotGui, weeklySnapshotGui, monthlySnapshotGui, separator, snapshotMount, snapshotUmount, snapshotRollback, snapshotDestroy, snapshotCreate]
