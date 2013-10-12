import os,subprocess

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import xbmcgui,xbmc

BACKUP_PROFILE = ['Daily','Weekly']

DEVICE = 'Device'
FILE  = 'File'

class homeBackupLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Home'))

class systemBackupLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','System'))

class systemBackup(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        #create the system settings
        #container with visibility condition
        #autoimage
        self.systemAutoBackup = RadioButtonControl(Tag('label','Auto image'))
        self.addControl(self.systemAutoBackup)
        self.multiDelta = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.systemAutoBackup.getId()))
        self.systemdeltaControl = SpinControlex(Tag('label',' -type'))
        for number in BACKUP_PROFILE :
            self.systemdeltaControl.addContent(Content(Tag('label',number),defaultSKin=False))
        self.multiDelta.addControl(self.systemdeltaControl)
        self.addControl(self.multiDelta)
        #Destination type (DEV/FILE) :
        self.systemBackupDestType = SpinControlex(Tag('label','Destination type '))
        self.addControl(self.systemBackupDestType)
        contentSD = Content(Tag('label',DEVICE),defaultSKin=False)
        self.systemBackupDestType.addContent(contentSD)
        contentSF = Content(Tag('label',FILE),defaultSKin=False)
        self.systemBackupDestType.addContent(contentSF)
        self.systemdevicePath = ButtonControl(Tag('label',' -Block device'),Tag('visible','Container(%d).HasFocus(%d)'%(self.systemBackupDestType.getWrapListId(),contentSD.getId())))
        self.systemdevicePath.onClick = lambda devicePath: self.systemdevicePath.setValue(self.getDevice())
        self.addControl(self.systemdevicePath)
        self.systemfilePath = ButtonControl(Tag('label',' -Dest folder'),Tag('visible','Container(%d).HasFocus(%d)'%(self.systemBackupDestType.getWrapListId(),contentSF.getId())))
        self.systemfilePath.onClick = lambda backupPath: self.systemfilePath.setValue(getFile('Backup Path',self.systemfilePath.getValue()))
        self.addControl(self.systemfilePath)
        self.ManualBackup = ButtonControl(Tag('label','Start backup now'))
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
    DIALOGHEADER = "System Backup"
    ERRORTEXT = "Error during updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self) :
        #override CB
        self.control.getDevice = self.getDevice
        self.control.startManualBackup = self.startManualBackup

    def startManualBackup(self):
        src = '/dev/root'       
        dialog = xbmcgui.Dialog()
        value = self.control.getValue()
        if value[1] == 'File' :
            rc = True
            value[2] = 'file:' + value[2]
        else :
            rc = dialog.yesno('***   WARNING   *** ','This action will ERASE ALL DATA on %s'%value[2],'If you don\'t know what you are doing, you shoud click No','                                       CONTINUE?')
        if rc :
            rc = xbianConfig('xbiancopy',src,value[2])
            wait = dialogWait('Backing up System','Backup system to %s'%value[2])
            wait.show()
            cont = True
            while cont  :
                rc = xbianConfig('xbiancopy','status')
                if rc :
                    rc = rc[0]
                    if rc == '0' :
                        #backup in progress
                        xbmc.sleep(1000)
                    elif rc == '1' :
                        #backup is finished
                        cont = False
                        msg ='Backup system is finished'
                    elif rc == '-1' :
                        cont = False
                        msg ='Something was wrong during copy'
                    elif rc == '-2' :
                        #shouldn't see this error
                        cont = False
                        msg ='backup not started'
                    else :
                        cont = False
                        msg ='Unexpected Error'
                else :
                    cont = False
                    msg ='Unexpected Error'             
            wait.close()
            xbmc.executebuiltin("Notification(%s,%s)"%(self.DIALOGHEADER,msg))
            wait.close()
            xbmc.executebuiltin("Notification(%s,%s)"%('Backup System',msg))
        return ''


    def getDevice(self) :
        dialog = xbmcgui.Dialog()
        #get a list of uuid here (maybe with size to prevent error)
        #Need a protection to not erase usb HDD with media?        
        uuid_list = subprocess.check_output(['udisks','--enumerate'])
        uuid_list  = filter(lambda x: len(x)>0, uuid_list.split('\n'))
        uuid_list  = map(lambda x: x.split('/')[-1], uuid_list)
        uuid_list  = filter(lambda x: x[:4] not in ('zram','mmcb'),uuid_list)
        uuid_list  = map(lambda x: '/dev/' + x, uuid_list)
        rc = dialog.select('Select Device',uuid_list)
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
        return [0,'File','',BACKUP_PROFILE[0]]

    def setXbianValue(self,value):
        #value is like [1,'File','/home/belese/', 'Daily']
        # or [1,'Device','UUID','Daily']
        #TODO
        #save xbian autobackup values here
        #return True if ok, False either
        print 'Save xbian :%s'%value
        return True

class homeBackup(Setting) :
    CONTROL = ButtonControl(Tag('label','Start Backup Now'))
    DIALOGHEADER = "Home Backup"
    ERRORTEXT = "Error during backup home"
    OKTEXT = "Home Backup is finished"

    def setControlValue(self,value) :
        pass

    def getUserValue(self):
        dialog = xbmcgui.Dialog()
        wait = dialogWait('Backing up Home','Home backup will be available on your samba share')
        wait.show()
        pid = xbianConfig('backuphome','start')        
        cont = True
        while cont  :
            rc = xbianConfig('backuphome','status')
            if rc :
                rc = rc[0]
                if rc == '0' :
                    #backup in progress
                    xbmc.sleep(1000)
                elif rc == '1' :
                    #backup is finished
                    cont = False
                    msg ='Backup Home is finished'
                elif rc == '-1' :
                    cont = False
                    msg ='Something was wrong during copy'
                elif rc == '-2' :
                    #shouldn't see this error
                    cont = False
                    msg ='backup not started'
                else :
                    cont = False
                    msg ='Unexpected Error'
            else :
                cont = False
                msg ='Unexpected Error'             
        wait.close()
        xbmc.executebuiltin("Notification(%s,%s)"%(self.DIALOGHEADER,msg))
        return ''

    def getXbianValue(self):
        return ''

    def setXbianValue(self,value):
        return ok


class backup(Category) :
    TITLE = 'Backup'
    SETTINGS = [homeBackupLabel,homeBackup,systemBackupLabel,AutoBackupGui]

