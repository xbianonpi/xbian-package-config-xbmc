from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

import os

from resources.lib.xbianconfig import xbianConfig

import xbmcgui

dialog=xbmcgui.Dialog()

class advancedLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Advanced'))

class advancedMode(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Advanced Mode'))
    DIALOGHEADER = "Advanced Mode"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"
    
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
        return rc
        
    def setXbianValue(self,value):
        self.setSetting(self.key,str(value))
        xbmc.executebuiltin('Skin.ToggleSetting(%s)'%self.key)
        return True

class notificationLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Notification'))

class notifyonError(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label','Notify on error'))
    DIALOGHEADER = "Notification on Error"
    def onInit(self) :
        self.key = 'notifyonerror'
    
class notifyonSuccess(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label','Notify on success'))
    DIALOGHEADER = "Notification on Success"
    def onInit(self) :
        self.key = 'notifyonsuccess'

class confirmonChange(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label','Ask Confirmation before save'))
    DIALOGHEADER = "Confirm Modification"
    
    def onInit(self) :
        self.key = 'confirmationonchange'

class UpdateLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Update'))

class updateonBoot(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label','Check update on boot'))
    DIALOGHEADER = "Notification on Error"
    def onInit(self) :
        self.key = 'updateonboot'

class updateTimer(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label','Check update every'))
    DIALOGHEADER = "Notification on Error"
    def onInit(self) :
        self.key = 'notifyonerror'

class updateAuto(advancedMode) :
    CONTROL = RadioButtonControl(Tag('label','Automatique Update'))
    DIALOGHEADER = "Notification on Error"
    def onInit(self) :
        self.key = 'updateauto'

#CATEGORY CLASS
class preference(Category) :
    TITLE = 'Preferences'
    SETTINGS = [advancedLabel,advancedMode,notificationLabel,confirmonChange,notifyonError,notifyonSuccess,UpdateLabel,updateonBoot,updateTimer,updateAuto]
    
    
