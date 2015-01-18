from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext

import xbmcgui

dialog=xbmcgui.Dialog()

class xbmcLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.xbmc.name')))

class xbmcTvOff(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.tvOffEnable = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.tvoff_screensaver')))
        self.addControl(self.tvOffEnable)
        self.tvOffProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.tvOffEnable.getId()))
        self.delay =  ButtonControl(Tag('label','        - %s'%_('xbian-config.xbmc.label.tvoff_screensaver_delay')))
        self.delay.onClick = lambda delay: self.delay.setValue(getNumeric(_('xbian-config.xbmc.label.tvoff_screensaver_delay'),self.delay.getValue(),0,60))
        self.tvOffProperty.addControl(self.delay)
        self.addControl(self.tvOffProperty)

    def setValue(self,value):
        self.tvOffEnable.setValue(value[0])
        self.delay.setValue(value[1])

class xbmcTvOffGui(Setting) :
    CONTROL = xbmcTvOff()
    DIALOGHEADER = _('xbian-config.xbmc.label.tvoff_screensaver')
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
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.tvon_exit')),ADVANCED)
    DIALOGHEADER = _('xbian-config.xbmc.label.tvon_exit')

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

class xbmcTvHaltOff(Setting) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.tvoff_shutdown')))
    DIALOGHEADER = _('xbian-config.xbmc.label.tvoff_shutdown')

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc =xbianConfig('xbmc','haltoff')
        return rc[0]

    def setXbianValue(self,value):
        rc =xbianConfig('xbmc','haltoff',str(value))
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class xbmcUSBLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.xbmc.label.usbhotplug')))

class xbmcUSBmount(Setting) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.automount')),ADVANCED)
    DIALOGHEADER = _('xbian-config.xbmc.label.automount')

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
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.share')))
    DIALOGHEADER = _('xbian-config.xbmc.label.share')

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
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.sharerw')))
    DIALOGHEADER = _('xbian-config.xbmc.label.sharerw')

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
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.uuid')),ADVANCED)
    DIALOGHEADER = _('xbian-config.xbmc.label.uuid')

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
        self.spinDownEnable = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.spindown')))
        self.addControl(self.spinDownEnable)
        self.spinDownProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.spinDownEnable.getId()))
        self.delay =  ButtonControl(Tag('label','        - %s'%_('xbian-config.xbmc.label.tvoff_screensaver_delay')))
        self.delay.onClick = lambda delay: self.delay.setValue(getNumeric(_('xbian-config.xbmc.label.tvoff_screensaver_delay'),self.delay.getValue(),0,20))
        self.spinDownProperty.addControl(self.delay)
        self.addControl(self.spinDownProperty)

    def setValue(self,value):
        self.spinDownEnable.setValue(value[0])
        self.delay.setValue(value[1])

class DynamicPriority(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.priorityEnable = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.dyn_priority')))
        self.addControl(self.priorityEnable)
        self.priorityProperty = MultiSettingControl(Tag('visible','SubString(Control.GetLabel(%d),*)'%self.priorityEnable.getId()))
        self.lowPriority =  ButtonControl(Tag('label','        - %s'%_('xbian-config.xbmc.label.lownice')))
        self.lowPriority.onClick = lambda lowPriority: self.lowPriority.setValue(getNumeric(_('xbian-config.xbmc.label.lownice'),self.lowPriority.getValue(),-19,20))
        self.highPriority =  ButtonControl(Tag('label','        - %s'%_('xbian-config.xbmc.label.highnice')))
        self.highPriority.onClick = lambda highPriority: self.highPriority.setValue(getNumeric(_('xbian-config.xbmc.label.highnice'),self.highPriority.getValue(),-19,20))
        self.priorityProperty.addControl(self.lowPriority)
        self.priorityProperty.addControl(self.highPriority)
        self.addControl(self.priorityProperty)

    def setValue(self,value):
        self.priorityEnable.setValue(value[0])
        self.lowPriority.setValue(value[1])
        self.highPriority.setValue(value[2])

class DynamicPriorityGui(Setting) :
    CONTROL = DynamicPriority(ADVANCED)
    DIALOGHEADER = _('xbian-config.xbmc.label.dyn_priority')
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
    DIALOGHEADER = _("xbian-config.xbmc.label.spindown")
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
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.xbmc.label.sync')),ADVANCED)
    DIALOGHEADER = _('xbian-config.xbmc.label.sync')

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
    TITLE = _('xbian-config.xbmc.name')
    SETTINGS = [xbmcLabel,xbmcTvOffGui,xbmcTvHaltOff,xbmcTvOn,DynamicPriorityGui,xbmcUSBLabel,xbmcUSBmount,xbmcUSBsync,xbmcUSBsmb,xbmcUSBsmbrw,xbmcUSBuuidname,SpinDownHddGui]
