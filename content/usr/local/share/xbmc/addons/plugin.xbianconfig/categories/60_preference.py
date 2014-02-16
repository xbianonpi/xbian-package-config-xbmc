from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext

import xbmcgui

dialog=xbmcgui.Dialog()

class advancedLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.preferences.label.advanced')))

class advancedMode(Setting) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.preferences.label.advanced_mode')))
    DIALOGHEADER = _('xbian-config.preferences.label.advanced_mode')
    
    def onInit(self) :
        self.key = 'advancedmode'
                    
    def getUserValue(self):
        return str(self.getControlValue())
    
    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)
    
    def getXbianValue(self):
        rc = self.getSetting(self.key)
        if rc == '1' :              
              setvisiblecondition(self.key,True)
        else :              
              setvisiblecondition(self.key,False)
        return rc
        
    def setXbianValue(self,value):
        self.setSetting(self.key,str(value))
        #xbmc.executebuiltin('Skin.ToggleSetting(%s)'%self.key)
        setvisiblecondition(self.key,value=='1')
        return True

class notificationLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.preferences.label.notify')))

class notifyonError(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.preferences.notify.on_error')))
    DIALOGHEADER = _('xbian-config.preferences.notify.on_error')
    def onInit(self) :
        self.key = 'notifyonerror'
    
class notifyonSuccess(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.preferences.notify.on_success')))
    DIALOGHEADER = _('xbian-config.preferences.notify.on_success')
    def onInit(self) :
        self.key = 'notifyonsuccess'

class confirmonChange(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.preferences.ask_confirmation')))
    DIALOGHEADER = _('xbian-config.preferences.ask_confirmation')
    
    def onInit(self) :
        self.key = 'confirmationonchange'


#CATEGORY CLASS
class preference(Category) :
    TITLE = 'Preferences'
    SETTINGS = [advancedLabel,advancedMode,notificationLabel,confirmonChange,notifyonError,notifyonSuccess]
    
    
