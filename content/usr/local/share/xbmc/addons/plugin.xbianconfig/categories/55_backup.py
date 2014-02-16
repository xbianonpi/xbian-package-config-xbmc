import os,subprocess
import datetime
import threading

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext


import xbmcgui,xbmc

BACKUP_PROFILE = ['daily','weekly','monthly']

DEVICE = 'Device'
FILE  = 'File'

DESTINATION_HOME_RESTORE = '/xbmc-backup/put_here_to_restore/'
class separator(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.backup.category.snasphot')))
class homeBackupLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.backup.category.home')))

class systemBackupLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.backup.category.system')))

class snapshotLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.backup.category.snapshot')))

class snapshotLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.backup.category.autosnapshot')))


class autodailysnapshot(MultiSettingControl):
    LABEL = _('xbian-config.backup.daily_snapshot')

    def onInit(self) :
        self.autodaily = RadioButtonControl(Tag('label',self.LABEL))
        self.addControl(self.autodaily)
        self.multiDelta = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.autodaily.getId()))
        self.countdaily = ButtonControl(Tag('label','     -%s'%_('xbian-config.backup.nbautosnap')))
        self.countdaily.onClick = lambda count: self.countdaily.setValue(getNumeric(_('xbian-config.backup.nbautosnap'),self.countdaily.getValue(),1,1000))
        self.multiDelta.addControl(self.countdaily)
        self.addControl(self.multiDelta)

    def getValue(self) :
        return [self.autodaily.getValue(),int(self.countdaily.getValue())]

    def setValue(self,value) :
        self.autodaily.setValue(value[0])
        self.countdaily.setValue(value[1])

class autoweeklysnapshot(autodailysnapshot):
    LABEL = _('xbian-config.backup.weekly_snapshot')

class systemBackup(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.systemAutoBackup = RadioButtonControl(Tag('label',_('xbian-config.backup.auto_system_image')))
        self.addControl(self.systemAutoBackup)
        self.multiDelta = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.systemAutoBackup.getId()))
        self.systemdeltaControl = SpinControlex(Tag('label',' -%s'%_('xbian-config.network.label.type')))
        for number in BACKUP_PROFILE :
            self.systemdeltaControl.addContent(Content(Tag('label',number),defaultSKin=False))
        self.multiDelta.addControl(self.systemdeltaControl)
        self.addControl(self.multiDelta)
        #Destination type (DEV/FILE) :
        self.systemBackupDestType = SpinControlex(Tag('label',_('xbian-config.backup.destype')))
        self.addControl(self.systemBackupDestType)
        contentSD = Content(Tag('label',DEVICE),defaultSKin=False)
        self.systemBackupDestType.addContent(contentSD)
        contentSF = Content(Tag('label',FILE),defaultSKin=False)
        self.systemBackupDestType.addContent(contentSF)
        self.systemdevicePath = ButtonControl(Tag('label',' -%s'%_('xbian-config.backup.blockdev')),Tag('visible','StringCompare(Skin.String(%s),%s)'%(self.systemBackupDestType.getKey(),DEVICE)))
        self.systemdevicePath.onClick = lambda devicePath: self.systemdevicePath.setValue(self.getDevice())
        self.addControl(self.systemdevicePath)
        self.systemfilePath = ButtonControl(Tag('label',' -%s'%_('xbian-config.xbiancopy.label.dest')),Tag('visible','StringCompare(Skin.String(%s),%s)'%(self.systemBackupDestType.getKey(),FILE)))
        self.systemfilePath.onClick = lambda backupPath: self.systemfilePath.setValue(getFile('Backup Path',self.systemfilePath.getValue())+getText('FileName','XBianImage.%s.img'%(datetime.datetime.now().strftime("%d-%m-%y"))))
        self.addControl(self.systemfilePath)
        self.ManualBackup = ButtonControl(Tag('label',_('xbian-config.backup.start')))
        self.ManualBackup.onClick = lambda manualback : self.startManualBackup()
        self.addControl(self.ManualBackup)
    def getDevice(self) :
        #to be override in gui - CB to display select dialog for ?UUID?
        pass

    def startManualBackup(self) :
        #to be override in gui - CB to startManualBackup
        pass

    def setValue(self,value):
        print value
        #by default, display system auto backup
        #
        #value = [
        #  1,   #system backup enable
        #  'Device'/'File',   #system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', #system Path
        #  BACKUP_PROFILE[x]#system backup delta
        # ]

        self.systemAutoBackup.setValue(value[0])
        self.systemBackupDestType.setValue(value[1])
        if value[1] == DEVICE :
            self.systemdevicePath.setValue(value[2])
        else :
            self.systemfilePath.setValue(value[2])
        self.systemdeltaControl.setValue(value[3])

    def getValue(self) :
        value = []
        value.append(self.systemAutoBackup.getValue())
        value.append(self.systemBackupDestType.getValue())
        if value[-1] == DEVICE :
            value.append(self.systemdevicePath.getValue())
        else :
            value.append(self.systemfilePath.getValue())
        value.append(self.systemdeltaControl.getValue())
        return value


class AutoBackupGui(Setting) :
    CONTROL = systemBackup(Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = _('xbian-config.backup.category.system')
        
    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self) :
        #override CB
        self.control.getDevice = self.getDevice
        self.control.startManualBackup = self.startManualBackup
        self.rc = 0

    def checkcopyFinish(self) :
        self.rc = xbianConfig('xbiancopy','status')[0]
        return self.rc != '0'

    def oncopyFinished(self) :
        if self.rc == '1' :
             #backup is finished
             self.OKTEXT = 'Backup system is finished'
             self.notifyOnSuccess()             
        else :
            if self.rc == '-1' :
                 self.ERRORTEXT = _('xbian-config.xbiancopy.dialog.preperror')
            elif self.rc == '-2' :
                 #shouldn't see this error
                 self.ERRORTEXT ='backup not started'
            else :
                 self.ERRORTEXT =_('xbian-config.dialog.unexpected_error')
            self.notifyOnError()            

    def startManualBackup(self):
        src = '/dev/root'
        dialog = xbmcgui.Dialog()
        value = self.control.getValue()
        if value[1] == 'File' :        
            value[2] = 'file:' + value[2]
            self.APPLYTEXT = _('xbian-config.backup.confirm_write')%value[2][5:]
            confirm = False
        else :
            self.APPLYTEXT = _('xbian-config.backup.warning_write')%value[2]
            confirm = True
                
        if self.askConfirmation(confirm) :
            rc = xbianConfig('xbiancopy','start',src,value[2])
            dlg = dialogWaitBackground('Xbian Copy',[_('xbian-config.backuphome.running')],self.checkcopyFinish,skinvar='systembackuprunning',onFinishedCB=self.oncopyFinished)
            dlg.show()
        return ''


    def getDevice(self) :
        dialog = xbmcgui.Dialog()
        #get a list of uuid here (maybe with size to prevent error)
        #Need a protection to not erase usb HDD with media?
        uuid_list = xbianConfig('xbiancopy','getpart')
        uuid_list  = filter(lambda x: len(x)>0, uuid_list[0].split(';'))
        rc = dialog.select(_('xbian-config.backup.selectdevice'),uuid_list)
        if rc == -1 :
           return self.xbianValue[2] #defaut device value in case of cancel
        else :
           return uuid_list[rc]

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        #value = [
        #  1/0,   #auto backup enable
        #  'Device'/'File',   #system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', #system Path
        #  BACKUP_PROFILE[x]#system backup delta
        # ]

        #TODO
        #read default Value from file here
        #value is like [1,'File','/home/belese/','Daily']
        if xbianConfig('xbiancopy','imgtype')[0] == 'file' :
           imgtype = 'File'
        else :
           imgtype = 'Device'
        delta = xbianConfig('xbiancopy','imgplan')
        if delta and delta[0] in BACKUP_PROFILE :
            delta = delta[0]
            actif = 1
        else :
            delta = BACKUP_PROFILE[0]
            actif = 0
        dest = xbianConfig('xbiancopy','imgdest')
        if dest :
            dest = dest[0]
        else :
            dest = ''
        return [actif,imgtype,dest,delta]

    def setXbianValue(self,value):
        #value is like [1,'File','/home/belese/', 'Daily']
        # or [1,'Device','UUID','Daily']
        #TODO
        #save xbian autobackup values here
        #return True if ok, False either
        if value[1] == 'File' : value[1] = 'file'
        if value[1] == 'Device' : value[1] = 'block'
        if value[0] == 0 : value[3] = 'none'
        if xbianConfig('xbiancopy','imgplan',value[3])[0] != '1' :
            return False
        if xbianConfig('xbiancopy','imgtype',value[1])[0] != '1' :
            return False
        if xbianConfig('xbiancopy','imgdest',value[2])[0] != '1' :
            return False
        return True

class homeBackup(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.backup.start')),Tag('enable','!skin.hasSetting(homebackuprunning)'))
    DIALOGHEADER = _('xbian-config.backup.category.home')
    
    def setControlValue(self,value) :
        pass

    def checkcopyFinish(self) :
        self.rc = xbianConfig('backuphome','status')[0]
        return self.rc != '0'

    def oncopyFinished(self) :
        if self.rc == '1' :
             #backup is finished
             self.OKTEXT = _('xbian-config.backuphome.done')
             self.notifyOnSuccess()             
        else :
            if self.rc == '-1' :
                 self.ERRORTEXT = _('xbian-config.backuphome.failed')
            elif self.rc == '-2' :
                 #shouldn't see this error
                 self.ERRORTEXT ='backup not started'
            else :
                 self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
            self.notifyOnError()            


    def getUserValue(self):
        self.APPLYTEXT = _('Backup /home to file')
        if self.askConfirmation() :
            pid = xbianConfig('backuphome','start')
            msg= [
            _('xbian-config.backuphome.desc1'),
            _('xbian-config.backuphome.desc2'),
            _('xbian-config.backuphome.desc3'),
            _('xbian-config.backuphome.desc4'),
            _('xbian-config.backuphome.desc5')]
            dlg = dialogWaitBackground(_('Backup /home to file'),msg,self.checkcopyFinish,skinvar='homebackuprunning',onFinishedCB=self.oncopyFinished)
            dlg.show()

    def getXbianValue(self):
        return ''

    def setXbianValue(self,value):
        return ok

class homeRestoreBackup(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.backuphome.restore')),Tag('enable','!skin.hasSetting(homebackuprunning)'))
    DIALOGHEADER = _('xbian-config.backuphome.restore')
    
    def setControlValue(self,value) :
        pass

    def checkcopyFinish(self) :
        return self.copyFileStatus != 0

    def oncopyFinished(self) :
        if self.copyFileStatus == -1 :
            self.notifyOnError()            
            return
        dialog = xbmcgui.Dialog().yesno('Reboot',_('xbian-config.main.reboot_question'))
        if dialog :
            xbmc.executebuiltin('Reboot')

    def copyThread(self,src,dest) :
        import xbmcvfs
        #copy is blocking, run in a thread for background dialog
        self.copyFileStatus = 0
        if xbmcvfs.copy(src,dest) :
           self.copyFileStatus = 1
        else :
           self.copyFileStatus = -1

    def getUserValue(self):
        src = xbmcgui.Dialog().browse(1,_('xbian-config.backuphome.selectimage'), 'files', '.img.gz')
        self.APPLYTEXT = _('xbian-config.backuphome.restore_home_confirm')%src        
        if src and self.askConfirmation() :
            #start thread copy
            copyT = threading.Thread(target=self.copyThread, args=(src,DESTINATION_HOME_RESTORE + '/xbianconfigrestore.img.gz'))
            copyT.start()
            msg= [_('xbian-config.backuphome.restore_home_info')]
            dlg = dialogWaitBackground(_('xbian-config.backuphome.restore'),msg,self.checkcopyFinish,skinvar='homebackuprunning',onFinishedCB=self.oncopyFinished)
            dlg.show()

    def getXbianValue(self):
        return ''

    def setXbianValue(self,value):
        return ok

class snapshotmount(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.snapshot.mountsnap')))
    DIALOGHEADER = _('xbian-config.backup.category.snapshot')        
    PROGRESSTEXT = _('xbian-config.common.pleasewait')
    BLAKLISTVOLUME = ['modules']
    

    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER,_('xbian-config.snapshot.loadingvolume'))
        load.show()
        volumeList = xbianConfig('listvol',cmd=['sudo','btrfs-auto-snapshot'])
        load.close()
        volumeList = list(set(volumeList)-set(self.BLAKLISTVOLUME))
        have_to_stop = False
        dialog = xbmcgui.Dialog()
        while not have_to_stop :
            volId = dialog.select(_('xbian-config.snapshot.volume'),volumeList)
            if volId == -1 :
               have_to_stop = True
            else :
                load = dialogWait(self.DIALOGHEADER,_('xbian-config.common.pleasewait'))
                load.show()
                snapshotList = xbianConfig('list',volumeList[volId],cmd=['sudo','btrfs-auto-snapshot'])
                snapshotList = filter(lambda x : x.split('@')[1],snapshotList)
                load.close()
                snapId = dialog.select('Snapshot',map(lambda x : x.split('@')[1],snapshotList))
                if snapId != -1 and self.askConfirmation() :
                    try :
                        dlg = dialogWait(self.DIALOGHEADER,self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(volumeList[volId],snapshotList[snapId])                        
                    except :
                        print 'error running btrfs-auto-spashot command %s %s'%(volumeList[volId],snapshotList[snapId])
                    finally :
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self,volume,snapshot) :
         #TODO check command
         mountdir = '/tmp/' + snapshot.split('/@')[0] + '@' + snapshot.split('/@')[1]
         if not os.path.isdir(mountdir):
            try :
                os.mkdir(mountdir)
            except :
                print 'XBian-Config : Cannot create mount dir : %s'%mountdir

         print xbianConfig('-t','btrfs','-o','subvol=%s'%snapshot,'/dev/root',mountdir,cmd=['sudo','/bin/mount'])

    def getXbianValue(self) :
        return ''

class snapshotRollback(snapshotmount) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.snapshot.rollback')))
    PROGRESSTEXT = _('xbian-config.common.pleasewait')    
    
    def runCmd(self,volume,snapshot) :
         print xbianConfig('rollback',snapshot,cmd=['sudo','btrfs-auto-snapshot'])
         dialog = xbmcgui.Dialog().yesno('Reboot',_('xbian-config.main.reboot_question'))
         if dialog :
            xbmc.executebuiltin('Reboot')

class snapshotDestroy(snapshotmount) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.snapshot.delete_snasphot')))
    PROGRESSTEXT = _('xbian-config.common.pleasewait')        
    
    def runCmd(self,volume,snapshot) :
        print xbianConfig('destroy',snapshot,cmd=['sudo','btrfs-auto-snapshot'])             

class snapshotCreate(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.snapshot.create_snapshot')))
    DIALOGHEADER = _('xbian-config.backup.category.snapshot')        
    BLAKLISTVOLUME = ['modules']
    PROGRESSTEXT = _('xbian-config.common.pleasewait')            
    
    def getUserValue(self):
        load = dialogWait(self.DIALOGHEADER,_('xbian-config.snapshot.loadingvolume'))
        load.show()        
        volumeList = xbianConfig('listvol',cmd=['sudo','btrfs-auto-snapshot'])
        load.close()        
        volumeList = list(set(volumeList)-set(self.BLAKLISTVOLUME))
        have_to_stop = False
        dialog = xbmcgui.Dialog()
        while not have_to_stop :
            volId = dialog.select('Volume',volumeList)
            if volId == -1 :
               have_to_stop = True
            else :
                snapshot = getText(_('xbian-config.snapshot.name_snapshot'),'btrfs-user-snap-%s'%datetime.datetime.now().strftime("%Y-%m-%d-%H%M"))
                if snapshot and self.askConfirmation() :
                    try :
                        dlg = dialogWait(self.DIALOGHEADER,self.PROGRESSTEXT)
                        dlg.show()
                        self.runCmd(volumeList[volId],snapshot)
                    except :
                        print 'error running btrfs-auto-spashot command %s %s'%(volumeList[volId],snapshot)
                    finally :
                        have_to_stop = True
                        dlg.close()
        return ''

    def runCmd(self,volume,snapshot) :
         #TODO check command
         print xbianConfig('snapshot','--name',snapshot,volume,cmd=['sudo','btrfs-auto-snapshot'])

    def getXbianValue(self) :
        return ''

class dailySnapshotGui(Setting) :
    CONTROL = autodailysnapshot()
    DIALOGHEADER = "Daily Snapshot"    
    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self) :
        self.key = 'dodaily'

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        rc= xbianConfig('xbiancopy',self.key)
        if rc :
            rc =rc[0].split(' ')
        if rc[0]=='0': rc.append(10)
        return map(int,rc)

    def setXbianValue(self,value):
        if value[0] == 1 :
           value = value[1]
        else :
           value = 0
        rc= xbianConfig('xbiancopy',self.key,str(value))
        if rc and rc[0] == '0' :
            return False
        else:
            return True

class weeklySnapshotGui(dailySnapshotGui) :
    CONTROL = autoweeklysnapshot()
    DIALOGHEADER = "Weekly Snapshot"

    def onInit(self) :
        self.key = 'doweekly'

class backup(Category) :
    TITLE = _('xbian-config.snapshot.backup')
    SETTINGS = [homeBackupLabel,homeBackup,homeRestoreBackup,systemBackupLabel,AutoBackupGui]
    #,snapshotLabel,dailySnapshotGui]
    #,weeklySnapshotGui,separator,snapshotmount,snapshotRollback,snapshotDestroy,snapshotCreate]

