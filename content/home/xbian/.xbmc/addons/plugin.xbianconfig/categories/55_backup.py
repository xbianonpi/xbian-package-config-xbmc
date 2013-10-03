import os
import subprocess
import time
import random
import string

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
import xbmcgui,xbmc
from xbmcaddon import Addon

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )


BACKUP_PROFILE = ['Daily','Weekly','Monthly']

DEVICE = 'Device'
FILE  = 'File'

class systemBackup(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Backup complete system (not functionnal yet)'))

class AutoBackup(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.backupType = SpinControlex(Tag('label','Source '))
        self.addControl(self.backupType)        
        contentS = Content(Tag('label','System'),defaultSKin=False)
        self.backupType.addContent(contentS)
        contentH = Content(Tag('label','Home'),defaultSKin=False)
        self.backupType.addContent(contentH)        
        
        #create the system settings
        #container with visibility condition
        self.systemSettingsMulti = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.backupType.getWrapListId(),contentS.getId())))
 
        #autoimage
        self.systemAutoBackup = RadioButtonControl(Tag('label','Auto image'))
        self.systemSettingsMulti.addControl(self.systemAutoBackup)
        self.systemAutoBackupMulti = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.systemAutoBackup.getId()))
        self.systemSettingsMulti.addControl(self.systemAutoBackupMulti)
        #Destination type (DEV/FILE) :
        self.systemdeltaControl = SpinControlex(Tag('label',' -type'))
        for number in BACKUP_PROFILE :
            self.systemdeltaControl.addContent(Content(Tag('label',number),defaultSKin=False))
        self.systemAutoBackupMulti.addControl(self.systemdeltaControl)                  
        self.systemBackupDestType = SpinControlex(Tag('label',' -Destination type '))
        self.systemAutoBackupMulti.addControl(self.systemBackupDestType)        
        contentSD = Content(Tag('label',DEVICE),defaultSKin=False)
        self.systemBackupDestType.addContent(contentSD)
        contentSF = Content(Tag('label',FILE),defaultSKin=False)
        self.systemBackupDestType.addContent(contentSF)                
        self.systemdevicePath = ButtonControl(Tag('label',' -block device'),Tag('visible','Container(%d).HasFocus(%d) + Container(%d).HasFocus(%d)'%(self.systemBackupDestType.getWrapListId(),contentSD.getId(),self.backupType.getWrapListId(),contentS.getId())))
        self.systemdevicePath.onClick = self.getDevice 
        self.systemAutoBackupMulti.addControl(self.systemdevicePath)
        self.systemfilePath = ButtonControl(Tag('label',' -Dest Name'),Tag('visible','Container(%d).HasFocus(%d) + Container(%d).HasFocus(%d)'%(self.systemBackupDestType.getWrapListId(),contentSF.getId(),self.backupType.getWrapListId(),contentS.getId())))
        self.systemfilePath.onClick = lambda backupPath: self.backupPath.setValue(getFile('Backup Path',self.systemfilePath.getValue()))
        self.systemAutoBackupMulti.addControl(self.systemfilePath)
        
        self.addControl(self.systemSettingsMulti)

        #create the home settings
        #container with visibility condition
        self.homeSettingsMulti = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.backupType.getWrapListId(),contentH.getId())))
 
        #autoimage
        self.homeAutoBackup = RadioButtonControl(Tag('label','Auto image'))
        self.homeSettingsMulti.addControl(self.homeAutoBackup)
        self.homeAutoBackupMulti = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.homeAutoBackup.getId()))
        self.homeSettingsMulti.addControl(self.homeAutoBackupMulti)
        #delta
        self.homedeltaControl = SpinControlex(Tag('label',' -type'))
        for number in BACKUP_PROFILE :
            self.homedeltaControl.addContent(Content(Tag('label',number),defaultSKin=False))
        self.homeAutoBackupMulti.addControl(self.homedeltaControl)                          
        #dest
        self.homefilePath = ButtonControl(Tag('label',' -Dest Name'))
        self.homefilePath.onClick = lambda backupPath: self.homefilePath.setValue(getFile('Backup Path',self.homefilePath.getValue()))
        self.homeAutoBackupMulti.addControl(self.homefilePath)
        
        self.addControl(self.homeSettingsMulti)


    def getDevice(self) :
        #to be override in gui - CB to display select dialog for ?UUID?
        pass
    def setValue(self,value):
        print value
        #by default, display system auto backup
        #        
        #value = [     
        # [
        #  1,   #system backup enable
        #  'Device'/'File',   #system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', #system Path
        #  BACKUP_PROFILE[x]#system backup delta
        # ],[ 
        #  1, #home backup enable
        #  'backup_dir', #backup home dir
        #  BACKUP_PROFILE[x]#home backup profile
        # ]] 
        
        #system
        self.backupType.setValue('System')
        self.systemAutoBackup.setValue(value[0][0])                        
        self.systemBackupDestType.setValue(value[0][1])
        if value[1] == DEVICE :
            self.systemdevicePath.setValue(value[0][2])
        else :
            self.systemfilePath.setValue(value[0][2])
        self.systemdeltaControl.setValue(value[0][3])
        #home
        self.homeAutoBackup.setValue(value[1][0])
        self.homefilePath.setValue(value[1][1])
        self.homedeltaControl.setValue(value[1][2])   

class AutoBackupGui(Setting) :
    CONTROL = AutoBackup(Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Auto Backup"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS    
        
    def onInit(self) :
        self.control.getDevice = self.getDevice
    
    def getDevice(self) :
        #display a select dialog with UUID device and return it as a string.        
        pass
        
    def getUserValue(self):
        values =  self.control.getValue()
        print 'Get user Value %s'%str(values)
        return values

    def getXbianValue(self):
        #value = [     
        # [
        #  1,   #system backup enable
        #  'Device'/'File',   #system destination type - if change need to be modif on content
        #  'UUID'/'backup_dir', #system Path
        #  BACKUP_PROFILE[x]#system backup delta
        # ],[ 
        #  1, #home backup enable
        #  'backup_dir', #backup home dir
        #  BACKUP_PROFILE[x]#home backup profile
        # ]] 
        #TODO
        #read default Value from file here
        #value is like [1, '/home/belese/', 'Daily']
        print 'Get xbian Value'
        #self.control.setEnabled(False)
        return [[1,'Device','FAKEUUID',BACKUP_PROFILE[0]],[0,'/temp',BACKUP_PROFILE[1]]]

    def setXbianValue(self,value):
        #TODO
        #save xbian value in file here
        #value is like [1, '/home/belese/', 'Daily']
        #return True if ok, False either
        print 'Save xbian :%s'%value
        return True

class backup(Category) :
    TITLE = 'Backup'
    SETTINGS = [systemBackup,AutoBackupGui]

