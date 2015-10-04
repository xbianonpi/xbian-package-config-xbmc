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


class systemBackup(MultiSettingControl):
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
        )) + getText('FileName', 'XBianImage.%s.img' % (datetime.datetime.now().strftime("%d-%m-%y"))))
        self.addControl(self.systemfilePath)
        self.ManualBackup = ButtonControl(Tag('label', _('Start backup now')))
        self.ManualBackup.onClick = lambda manualback: self.startManualBackup()
        self.addControl(self.ManualBackup)

    def getDevice(self):
        # to be override in gui - CB to display select dialog for ?UUID?
        pass

    def startManualBackup(self):
        # to be override in gui - CB to startManualBackup
        pass

    def setValue(self, value):
        print value
        # by default, display system auto backup
        #
        # value = [
        #  1,   #system backup enable
        #  'Device'/'File',   #system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', #system Path
        #  BACKUP_PROFILE[x]#system backup delta
        # ]

        self.systemAutoBackup.setValue(value[0])
        self.systemBackupDestType.setValue(value[1])
        if value[1] == DEVICE:
            self.systemdevicePath.setValue(value[2])
        else:
            self.systemfilePath.setValue(value[2])
        self.systemdeltaControl.setValue(value[3])

    def getValue(self):
        value = []
        value.append(self.systemAutoBackup.getValue())
        value.append(self.systemBackupDestType.getValue())
        if value[-1] == DEVICE:
            value.append(self.systemdevicePath.getValue())
        else:
            value.append(self.systemfilePath.getValue())
        value.append(self.systemdeltaControl.getValue())
        return value


class AutoBackupGui(Setting):
    CONTROL = systemBackup(ADVANCED)
    DIALOGHEADER = _('System backup')

    SAVEMODE = Setting.ONUNFOCUS

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
            self.OKTEXT = 'Backup system is finished'
            self.notifyOnSuccess()
        else:
            if self.rc == '-1':
                self.ERRORTEXT = _("Can't prepare destination filesystem")
            elif self.rc == '-2':
                # shouldn't see this error
                self.ERRORTEXT = 'backup not started'
            else:
                self.ERRORTEXT = _('An unexpected error occurred')
            self.notifyOnError()

    def startManualBackup(self):
        value = self.control.getValue()
        if value[1] == 'File':
            value[2] = 'file:' + value[2]
            self.APPLYTEXT = _('Write backup to %s?') % (value[2][5:], )
            confirm = False
        else:
            self.APPLYTEXT = _('This will erase ALL data on %s, continue?') % (
                value[2], )
            confirm = True

        if self.askConfirmation(confirm):
            dlg = dialogWaitBackground(
                'Xbian Copy', [_('Please wait while creating backup file')],
                self.checkcopyFinish,
                skinvar='systembackuprunning',
                onFinishedCB=self.oncopyFinished)
            dlg.show()
        return ''

    def getDevice(self):
        dialog = xbmcgui.Dialog()
        # get a list of uuid here (maybe with size to prevent error)
        # Need a protection to not erase usb HDD with media?
        uuid_list = xbianConfig('xbiancopy', 'getpart')
        uuid_list = filter(lambda x: len(x) > 0, uuid_list[0].split(';'))
        rc = dialog.select(_('Select Device'), uuid_list)
        if rc == -1:
            return self.xbianValue[2]  # defaut device value in case of cancel
        else:
            return uuid_list[rc]

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        # value = [
        #  1/0,   #auto backup enable
        #  'Device'/'File',   #system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', #system Path
        #  BACKUP_PROFILE[x]#system backup delta
        # ]

        # TODO
        # read default Value from file here
        # value is like [1,'File','/home/belese/','Daily']
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
        return [actif, imgtype, dest, delta]

    def setXbianValue(self, value):
        # value is like [1,'File','/home/belese/', 'Daily']
        # or [1,'Device','UUID','Daily']
        # TODO
        # save xbian autobackup values here
        # return True if ok, False either
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
        return True


class homeBackup(Setting):
    CONTROL = ButtonControl(
        Tag('label', _('Start backup now')),
        Tag('enable', '!%s' % (visiblecondition('homebackuprunning'), )))
    DIALOGHEADER = _('Home backup')

    def setControlValue(self, value):
        pass

    def checkcopyFinish(self):
        self.rc = xbianConfig('backuphome', 'status')[0]
        return self.rc != '0'

    def oncopyFinished(self):
        if self.rc == '1':
            # backup is finished
            self.OKTEXT = _(
                "Backup file is prepared at /xbmc-backup. "
                "Please grab the file over network or save locally.")
            self.notifyOnSuccess()
        else:
            if self.rc == '-1':
                self.ERRORTEXT = _('Backup /home process failed!')
            elif self.rc == '-2':
                # shouldn't see this error
                self.ERRORTEXT = 'backup not started'
            else:
                self.ERRORTEXT = _('An unexpected error occurred')
            self.notifyOnError()

    def getUserValue(self):
        self.APPLYTEXT = _('Backup /home to file')
        if self.askConfirmation():
            msg = [
                _('It can take several minutes depending on size of your '
                  '/home/xbian directory'),
                _('File will be created under /xbian-backup, which is also '
                  'accessible through smb share'),
                _('Until finished, there will be just temp folder. '
                  'Once ready, .img file will appear.'),
                _('You can copy the file directly to you computer '
                  '(the file will be deleted during reboots!)'),
                _('To restore your XBMC, just copy .img file to '
                  '/xbian-backup/put_to_restore folder.'),
            ]
            dlg = dialogWaitBackground(
                _('Backup /home to file'),
                msg,
                self.checkcopyFinish,
                skinvar='homebackuprunning',
                onFinishedCB=self.oncopyFinished)
            dlg.show()

    def getXbianValue(self):
        return ''

    def setXbianValue(self, value):
        return ok


class homeRestoreBackup(Setting):
    CONTROL = ButtonControl(
        Tag('label', _('Restore backup')),
        Tag('enable', '!%s' % (visiblecondition('homebackuprunning'), )))
    DIALOGHEADER = _('Restore backup')

    def setControlValue(self, value):
        pass

    def checkcopyFinish(self):
        return self.copyFileStatus != 0

    def oncopyFinished(self):
        if self.copyFileStatus == -1:
            self.notifyOnError()
            return
        dialog = xbmcgui.Dialog().yesno(
            'Reboot', _('A reboot is required. Do you want to reboot now?'))
        if dialog:
            xbmc.executebuiltin('Reboot')

    def copyThread(self, src, dest):
        import xbmcvfs
        # copy is blocking, run in a thread for background dialog
        self.copyFileStatus = 0
        if xbmcvfs.copy(src, dest):
            self.copyFileStatus = 1
        else:
            self.copyFileStatus = -1

    def getUserValue(self):
        src = xbmcgui.Dialog().browse(
            1, _('Select Home Image'), 'files', '.img.gz')
        self.APPLYTEXT = _('%s : Do you want to restore home from %s?') % (src, )
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
                self.checkcopyFinish,
                skinvar='homebackuprunning',
                onFinishedCB=self.oncopyFinished)
            dlg.show()

    def getXbianValue(self):
        return ''

    def setXbianValue(self, value):
        return ok


class snapshotmount(Setting):
    CONTROL = ButtonControl(Tag('label', _('Mount a snapshot')), ADVANCED)
    DIALOGHEADER = _('Snapshot')
    PROGRESSTEXT = _('Please wait...')
    BLAKLISTVOLUME = ['modules']

    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER, _('Loading volumes...'))
        load.show()
        volumeList = xbianConfig('listvol', cmd=['sudo', 'btrfs-auto-snapshot'])
        load.close()
        volumeList = list(set(volumeList) - set(self.BLAKLISTVOLUME))
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
                snapshotList = filter(lambda x: x.split('@')[1], snapshotList)
                load.close()
                snapId = dialog.select('Snapshot', map(lambda x: x.split('@')[1], snapshotList))
                if snapId != -1 and self.askConfirmation():
                    try:
                        dlg = dialogWait(self.DIALOGHEADER, self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(volumeList[volId], snapshotList[snapId])
                    except:
                        print 'error running btrfs-auto-spashot command %s %s' % (volumeList[volId], snapshotList[snapId])
                    finally:
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self, volume, snapshot):
        # TODO check command
        mountdir = '/tmp/' + snapshot.split('/@')[0] + '@' + snapshot.split('/@')[1]
        if not os.path.isdir(mountdir):
            try:
                os.mkdir(mountdir)
            except:
                print 'XBian-Config : Cannot create mount dir : %s' % mountdir

        print xbianConfig('-t', 'btrfs', '-o', 'subvol=%s' % snapshot, '/dev/root', mountdir, cmd=['sudo', '/bin/mount'])

    def getXbianValue(self):
        return ''


class snapshotRollback(snapshotmount):
    CONTROL = ButtonControl(Tag('label', _('Rollback to a snapshot')))
    PROGRESSTEXT = _('Please wait...')

    def runCmd(self, volume, snapshot):
        print xbianConfig('rollback', snapshot, cmd=['sudo', 'btrfs-auto-snapshot'])
        dialog = xbmcgui.Dialog().yesno(
            'Reboot', _('A reboot is required. Do you want to reboot now?'))
        if dialog:
            xbmc.executebuiltin('Reboot')


class snapshotDestroy(snapshotmount):
    CONTROL = ButtonControl(Tag('label', _('Delete a snapshot')), ADVANCED)
    PROGRESSTEXT = _('Please wait...')

    def runCmd(self, volume, snapshot):
        print xbianConfig('destroy', snapshot, cmd=['sudo', 'btrfs-auto-snapshot'])


class snapshotCreate(Setting):
    CONTROL = ButtonControl(Tag('label', _('Create a snapshot')))
    DIALOGHEADER = _('Snapshot')
    BLAKLISTVOLUME = ['modules']
    PROGRESSTEXT = _('Please wait...')

    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER, _('Loading volumes...'))
        load.show()
        volumeList = xbianConfig('listvol', cmd=['sudo', 'btrfs-auto-snapshot'])
        load.close()
        volumeList = list(set(volumeList) - set(self.BLAKLISTVOLUME))
        have_to_stop = False
        dialog = xbmcgui.Dialog()
        while not have_to_stop:
            volId = dialog.select('Volume', volumeList)
            if volId == -1:
                have_to_stop = True
            else:
                snapshot = getText(
                    _('Snapshot name'),
                    'btrfs-user-snap-%s' % (
                        datetime.datetime.now().strftime("%Y-%m-%d-%H%M"), ))
                if snapshot and self.askConfirmation():
                    try:
                        dlg = dialogWait(self.DIALOGHEADER, self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(volumeList[volId], snapshot)
                    except:
                        print 'error running btrfs-auto-spashot command %s %s' % (volumeList[volId], snapshot)
                    finally:
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self, volume, snapshot):
        # TODO check command
        print xbianConfig('snapshot', '--name', snapshot, volume, cmd=['sudo', 'btrfs-auto-snapshot'])

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
        return map(int, rc)

    def setXbianValue(self, value):
        if value[0] == 1:
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


class backup(Category):
    TITLE = _('Backup')
    SETTINGS = [homeBackupLabel, homeBackup, homeRestoreBackup, systemBackupLabel, AutoBackupGui, snapshotLabel,
                dailySnapshotGui, weeklySnapshotGui, separator, snapshotmount, snapshotRollback, snapshotDestroy, snapshotCreate]
