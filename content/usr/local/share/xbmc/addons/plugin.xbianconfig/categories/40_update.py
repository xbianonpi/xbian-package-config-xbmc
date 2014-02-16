import os
import time
import random
import string

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext


import xbmc
from xbmcaddon import Addon

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

APTLOGFILE = '/tmp/aptstatus'
#disable settings that need apt while installing/updating
SKINVARAPTRUNNIG = 'aptrunning'
KEYFORCECHECK = 'enableForce'

class updateControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
   
    def onInit(self) :
        char_set = string.ascii_lowercase
        self.key = ''.join(random.sample(char_set,6))
        self.keyupdateall = '%sall'%self.key
        self.nbUpdate = 15
        self.nbcanbeupdate = 0
        self.updates = []
        for i in range(self.nbUpdate) :
            self.updates.append({})
        
        keynoupdate = ''
        for i,update in enumerate(self.updates) :                                    
            update['name'] = ButtonControl(Tag('visible','skin.hasSetting(%s%d)'%(self.key,i)),Tag('enable','!skin.hasSetting(%s)'%SKINVARAPTRUNNIG))
            update['name'].onClick = lambda update : self.onUpdateClick(self.getCurrentUpdate(update))
            self.addControl(update['name'])
            keynoupdate+='!Control.IsVisible(%d) + '%update['name'].getId()
        keynoupdate = keynoupdate[:-3]        
        self.udpateAll = ButtonControl(Tag('label','Update all'),Tag('visible','skin.hasSetting(%s)'%self.keyupdateall),Tag('enable','!skin.hasSetting(%s)'%SKINVARAPTRUNNIG))
        self.udpateAll.onClick = lambda updateall : self.onUpdateAll()
        self.addControl(self.udpateAll)

        xbmc.executebuiltin('Skin.Reset(%s)'%KEYFORCECHECK)
        self.forceCheck = ButtonControl(Tag('label',_('xbian-config.updatemenu.description')),Tag('visible','skin.hasSetting(%s)'%KEYFORCECHECK),Tag('enable','!skin.hasSetting(%s)'%SKINVARAPTRUNNIG))
        self.forceCheck.onClick = lambda forcecheck : self.onForceCheck()
        self.addControl(self.forceCheck)

        self.udpateNo = ButtonControl(Tag('label',''),Tag('visible','%s'%keynoupdate))
        self.addControl(self.udpateNo)

    def getCurrentUpdate(self,control):
        for i,update in enumerate(self.updates) :
            if update['name'] == control :
                return i+1
            
    def addUpdate(self,update) :        
        values = update.split(';')        
        self.updates[int(values[0])-1]['name'].setLabel(values[1])
        self.updates[int(values[0])-1]['name'].setValue(values[3])
        xbmc.executebuiltin('Skin.SetBool(%s%d)'%(self.key,int(values[0])-1))
        self.nbcanbeupdate += 1
        if self.nbcanbeupdate == 2 :
            xbmc.executebuiltin('Skin.SetBool(%s)'%self.keyupdateall)
        elif self.nbcanbeupdate == 1 :
            xbmc.executebuiltin('Skin.Reset(%s)'%self.keyupdateall)
    
    def removeUpdate(self,update)  :   
        values = update.split(';')
        xbmc.executebuiltin('Skin.Reset(%s%d)'%(self.key,int(values[0])-1))
        self.nbcanbeupdate -= 1
        if self.nbcanbeupdate == 1 :
            xbmc.executebuiltin('Skin.Reset(%s)'%self.keyupdateall)

    def onUpdateClick(self,updateId) :
        pass

    def onUpdateAll(self) :
        pass

    def onForceCheck(self) :
        pass
        
class upgradeXbianLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.updates.label.updates')))      

class packageUpdate(Setting) :
    CONTROL = updateControl()
    DIALOGHEADER = _('xbian-config.updates.label.updates')
    ERRORTEXT = _('xbian-config.updates.update.error')
    OKTEXT = _('xbian-config.updates.update.success')
    APPLYTEXT = _('xbian-config.updates.update.confirm')

    def onInit(self) :
        self.control.onUpdateClick = self.onUpdate       
        self.control.onUpdateAll = self.onUpdateAll
        self.control.onForceCheck = self.onForceCheck
        self.keyword()
    
    def keyword(self) :
        self.key = 'packages'
                           
    def checkUpdateFinish(self) :        
        return xbianConfig('updates','progress')[0] != '1'
        
    def onUpdateFinished(self) :
        os.remove(self.lockfile) 
        #refresh gui
        #remove settings from gui
        for update in self.xbianValue :                     
              self.control.removeUpdate(update)
        #reload value
        self.xbianValue = self.getXbianValue()                  
        self.notifyOnSuccess()
    
    def onUpdate(self,updateId):        
        self.lockfile = '/var/lock/.%s'%self.key
        open(self.lockfile,'w').close()
        updateId = str(updateId)        
        if self.askConfirmation(True) :
            rc =xbianConfig('updates','install',self.key,updateId)
            if rc and rc[0] == '1' :                
                dlg = dialogWaitBackground(self.DIALOGHEADER,[],self.checkUpdateFinish,APTLOGFILE,skinvar=SKINVARAPTRUNNIG,onFinishedCB=self.onUpdateFinished)
                dlg.show()              
            else :
                if rc and rc[0] == '2' :
                    self.ERRORTEXT = _('xbian-config.updates.update.already_installed')           
                elif rc and rc[0] == '3' :
                    self.ERRORTEXT = _('xbian-config.updates.update.not_exists')
                elif rc and rc[0] == '4' :
                    self.ERRORTEXT = _('xbian-config.updates.update.not_exists')
                elif rc and rc[0] == '5' :
                    self.ERRORTEXT = _('xbian-config.updates.update.size_mismatch')
                elif rc and rc[0] == '6' :
                    self.ERRORTEXT = _('xbian-config.updates.update.error')
                else :
                    self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
                os.remove(self.lockfile)                
                self.notifyOnError()    
            
    def onForceCheck(self) :
        xbmc.executebuiltin('Skin.SetBool(%s)'%SKINVARAPTRUNNIG)
        self.lockfile = '/var/lock/.%s'%self.key
        open(self.lockfile,'w').close()

        progress = dialogWait(_('xbian-config.common.pleasewait'),_('xbian-config.updates.list.download'))
        progress.show()
        rc = xbianConfig('updates','updatedb')
        progress.close()

        if rc and rc[0] == '1' :
            self.onUpdateFinished()
        xbmc.executebuiltin('Skin.Reset(%s)'%SKINVARAPTRUNNIG)

    def onUpdateAll(self) :
        updates = '-'        
        self.onUpdate(updates)
        
    def getXbianValue(self):
        rc =xbianConfig('updates','list',self.key)
        if rc and rc[0] not in ('0','-2') : 
            for update in rc[:15] :
                self.control.addUpdate(update)
        else :
            self.control.udpateNo.setLabel(_('xbian-config.updates.label.update_to_date'))

        xbmc.executebuiltin('Skin.SetBool(%s)'%KEYFORCECHECK)
        return rc

class updatePackageLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.updates.label.updates')))      

class UpdateLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.updates.label.autoupdates')))
        
class updateAuto(Setting) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.updates.label.autoinstallupdates')))
    DIALOGHEADER = _('xbian-config.updates.label.autoupdates')
    
    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('updates','enableauto')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('updates','enableauto',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class snapAPT(Setting) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.updates.label.aptsnapshot')))
    DIALOGHEADER = _('xbian-config.updates.label.update')
    
    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('updates','snapapt')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('updates','snapapt',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class InventoryInt(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.AutoInventory = RadioButtonControl(Tag('label',_('xbian-config.updates.label.autoupdaterepo')))
        self.addControl(self.AutoInventory)
        self.AutoInventoryProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.AutoInventory.getId()))
        self.delay =  ButtonControl(Tag('label','        - %s'%_('xbian-config.updates.label.autoupdaterepointerval')))
        self.delay.onClick = lambda delay: self.delay.setValue(getNumeric(_('xbian-config.updates.label.autoupdaterepointerval'),self.delay.getValue(),1,365))
        self.AutoInventoryProperty.addControl(self.delay)
        self.addControl(self.AutoInventoryProperty)
    
    def setValue(self,value):
        self.AutoInventory.setValue(value[0])
        self.delay.setValue(value[1])

class InventoryIntGui(Setting) :
    CONTROL = InventoryInt()
    DIALOGHEADER = _('xbian-config.updates.label.autoupdaterepo')    
    SAVEMODE = Setting.ONUNFOCUS
    
    def getUserValue(self):
        values =  self.control.getValue()
        return values

    def getXbianValue(self):
        rc =xbianConfig('updates','autoinventory')
        r =rc[0].split(' ')
        return [int(r[0]), r[1]]

    def setXbianValue(self,value):
        rc =xbianConfig('updates','autoinventory',str(value[0]),str(value[1]))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class emptyLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',''))

class update(Category) :
    TITLE = _('xbian-config.updates.label.update')
    SETTINGS = [updatePackageLabel,packageUpdate,UpdateLabel,InventoryIntGui,updateAuto,snapAPT]
