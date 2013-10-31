from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import xbmcgui

dialog=xbmcgui.Dialog()

class xbmcLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Xbmc'))

class xbmcGui(Setting) :
    CONTROL = SpinControlex(Tag('label','XBMC GUI resolution'))
    DIALOGHEADER = "XBMC GUI resolution"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS
    
    def onInit(self):
        resolutionlist =xbianConfig('xbmc','guires','list')
        if resolutionlist :
            for resolution in resolutionlist :
                content = Content(Tag('label','%sp'%resolution),defaultSKin=False)
                self.control.addContent(content)

    def getUserValue(self):
        return self.control.getValue()
        
    def getXbianValue(self):
        resolution =xbianConfig('xbmc','guires','select')
        if resolution :
            return '%sp'%resolution[0]
        else :
            return ''                
        
    def setXbianValue(self,value):
        value = value[:-1]
        rc = xbianConfig('xbmc','guires','update',value)
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcTvOff(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.tvOffEnable = RadioButtonControl(Tag('label','Turn CEC capable TV OFF with screensaver'))
        self.addControl(self.tvOffEnable)
        self.tvOffProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.tvOffEnable.getId()))
        self.delay =  ButtonControl(Tag('label','        - delay (min)'))
        self.delay.onClick = lambda delay: self.delay.setValue(getNumeric('delay (min)',self.delay.getValue(),0,60))
        self.tvOffProperty.addControl(self.delay)
        self.addControl(self.tvOffProperty)

    def setValue(self,value):
        self.tvOffEnable.setValue(value[0])
        self.delay.setValue(value[1])

class xbmcTvOffGui(Setting) :
    CONTROL = xbmcTvOff()
    DIALOGHEADER = "Turn off TV with screensaver"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        values =  self.control.getValue()
        return values

    def getXbianValue(self):
        rc =xbianConfig('xbmc','tvoff')
        r =rc[0].split(' ')
        return [int(r[0]), r[1]]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','tvoff',str(value[0]),str(value[1]))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcTvOn(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Turn CEC capable TV ON when XBMC exit'))
    DIALOGHEADER = "TV ON exit"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','tvexiton')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','tvexiton',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcUSBLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','USB HotPlug'))

class xbmcUSBmount(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Enable USB disk automounting'))
    DIALOGHEADER = "USB automount"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','usbauto')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','usbauto',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcUSBsmb(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Make automounted disks available via SMB'))
    DIALOGHEADER = "USB sharing"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','usbshare')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','usbshare',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcUSBsmbrw(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Shares should be world  writable (including anonymous access)'))
    DIALOGHEADER = "USB shares writable"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','sharerw')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','sharerw',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False


class xbmcUSBuuidname(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Include partition UUID in mnt folder name'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "UUID in folder name"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','uuidname')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','uuidname',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class SpinDownHdd(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.spinDownEnable = RadioButtonControl(Tag('label','Spin down HDD'))
        self.addControl(self.spinDownEnable)
        self.spinDownProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.spinDownEnable.getId()))
        self.delay =  ButtonControl(Tag('label','        - delay (min)'))
        self.delay.onClick = lambda delay: self.delay.setValue(getNumeric('delay (min)',self.delay.getValue(),0,20))
        self.spinDownProperty.addControl(self.delay)
        self.addControl(self.spinDownProperty)

    def setValue(self,value):
        self.spinDownEnable.setValue(value[0])
        self.delay.setValue(value[1])

class DynamicPriority(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.priorityEnable = RadioButtonControl(Tag('label','XBMC Dynamic Priority'))
        self.addControl(self.priorityEnable)
        self.priorityProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.priorityEnable.getId()))
        self.lowPriority =  ButtonControl(Tag('label','        - Xbmc low priority'))
        self.lowPriority.onClick = lambda lowPriority: self.lowPriority.setValue(getNumeric('Low Nice priority',self.lowPriority.getValue(),-19,20))
        self.highPriority =  ButtonControl(Tag('label','        - Xbmc high priority'))
        self.highPriority.onClick = lambda highPriority: self.highPriority.setValue(getNumeric('Low Nice priority',self.highPriority.getValue(),-19,20))
        self.priorityProperty.addControl(self.lowPriority)
        self.priorityProperty.addControl(self.highPriority)
        self.addControl(self.priorityProperty)

    def setValue(self,value):
        self.priorityEnable.setValue(value[0])
        self.lowPriority.setValue(value[1])
        self.highPriority.setValue(value[2])

class DynamicPriorityGui(Setting) :
    CONTROL = DynamicPriority(Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Dynamic process priority"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        values =  self.control.getValue()
        return values

    def getXbianValue(self):
        rc =xbianConfig('xbmc','priority')
        r =rc[0].split(' ')
        return [int(r[0]), r[1], r[2]]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','priority',str(value[0]),str(value[1]),str(value[2]))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class SpinDownHddGui(Setting) :
    CONTROL = SpinDownHdd()
    DIALOGHEADER = "Spin Down HDD"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        values =  self.control.getValue()
        return values

    def getXbianValue(self):
        rc =xbianConfig('xbmc','hddspin')
        r =rc[0].split(' ')
        return [int(r[0]), r[1]]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','hddspin',str(value[0]),str(value[1]))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcUSBsync(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Mount with sync option'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "USB sync"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','usbsync')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','usbsync',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

#CATEGORY CLASS
class xbmc(Category) :
    TITLE = 'XBMC'
    SETTINGS = [xbmcLabel,xbmcGui,xbmcTvOffGui,xbmcTvOn,DynamicPriorityGui,xbmcUSBLabel,xbmcUSBmount,xbmcUSBsync,xbmcUSBsmb,xbmcUSBsmbrw,xbmcUSBuuidname,SpinDownHddGui]
