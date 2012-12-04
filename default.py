# -*- coding: cp1252 -*-

__script__       = "Unknown"
__plugin__       = "xbian config"
__addonID__      = "script.program.xbian"
__author__       = "Belese(http://www.xbian.org)"
__url__          = "http://www.xbian.org"
__credits__      = "Xbian"
__platform__     = "xbmc media center"
__date__         = "30-11-2012"
__version__      = "0.0.1"


import os
import itertools
import fnmatch
import shutil
import threading
# xbmc modules
import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon
from elementtree.ElementTree import *

#addon module
from resources.lib.api import APIget,APIset

 
ADDON     = Addon( __addonID__ )
Language  = ADDON.getLocalizedString
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString


ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )

ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7

ID_BUTTON_OK = 11
ID_BUTTON_CANCEL = 10

class Window(xbmcgui.WindowXMLDialog):
    pass
    
class Setting():
    id_generator = itertools.count(60000)
    def __init__(self,key,control_level=0):
        self.id = next(self.id_generator)
        self.active = False
        self.control = None
        self.key = key
        control_level = 0
        if self.key[:1].isdigit() :
            control_level = int(self.key[:1])
            self.APIkey = self.key[1:]
        else:
            self.APIkey = self.key
        self.control_level = control_level
        #change here to get setting from api and set setting in xbmc
        if self.control_level == 0 :
            self.value = APIget.dispatch(self.APIkey)
        else :
            self.value = APIget.subSetting(self.APIkey)
        #update xbmc data with xbian data
        ADDON.setSetting(self.key,self.value)
    
    def isUpdated(self) :
        return self.value != ADDON.getSetting(self.key)
    
    def update(self) :
        self.value = ADDON.getSetting(self.key)
        print self.value
    
    def updateXbian(self,data) :
        #call xbian dispatcher function
        rc = APIset.dispatch(self.APIkey,data)
        
    def getControlLevel(self):
        return self.control_level
    
    def getControl(self,xmlDialogWindow) :
        print xmlDialogWindow
        self.control = xmlDialogWindow.getControl(self.id)
        
    def isEnabled(self) :
        if self.control :
            return not self.control.isSelected()
        return False
    
    def setActive(self,active):
        self.active = active
    
    def isActive(self):
        return self.active
        
    def getValue(self) :
        return self.value
    
    def getKey(self) :
        return self.key
    
    def getRadioButtonXml(self):
        self.update()
        if self.getControlLevel() == 0 :
            xml =  '<control type="radiobutton" id="%d">\n'%self.id
        else :
            xml =  '<control type="label" id="%d">\n'%self.id
        xml += '<description>update confirmation : %s</description>\n'%self.key
        xml += '<width>550</width>\n'
        xml += '<height>30</height>\n'
        xml += '<aligny>center</aligny>\n'
        xml += '<textureradioon>radiobutton-nofocus.png</textureradioon>'
        xml += '<textureradiooff>radiobutton-focus.png</textureradiooff>'
        #xml += '<selected>true</selected>'
        #not clean -modif later
        tab =""
        for i in range(self.getControlLevel()):
            tab += "     "
        xml += '<label>%s%s set to %s</label>\n'%(tab,self.APIkey,self.value)
        xml += '</control>\n'
        return xml

class Settings() :
    def __init__(self) :
        self.settings = []
        #read default settings here 
        self.getDefaults()
        self.getCategories()
        self.createSettingsXMl()
        self.getXMLControl()
    
    def onAction(self,action):
        print action
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        pass
    
    def onClick(self,controlId) :
        if controlId == ID_BUTTON_OK :
            settings.applyXbianUpdate()
            self.close()
        elif controlId == ID_BUTTON_CANCEL :
            self.close()

    
    def close(self) :
        #Set Standard addon_config
        self.window.close()
        #shutil.copy2(os.path.join(BASE_RESOURCE_PATH,'settings_addon.xml'),os.path.join(BASE_RESOURCE_PATH,'settings.xml'))
        
    def getCategories(self) :
        self.catdir = os.path.join(BASE_RESOURCE_PATH,'category')
        self.categoryXMLfiles = []
        for file in os.listdir(self.catdir):
            if fnmatch.fnmatch(file, '*.xml'):
                self.categoryXMLfiles.append(file)
        self.categoryXMLfiles.sort()
        
    def createSettingsXMl(self) :
        print 'yaaaaaaaaaaaaaaaa'
        settingXml = open(os.path.join(BASE_RESOURCE_PATH,'settings.xml'),'w')
        settingXml.write('<settings>\n');
        for category in self.categoryXMLfiles :
            categoryXml = open(os.path.join(self.catdir,category))
            for line in categoryXml :
                #check here if special control
                settingXml.write(line)
                print line
            categoryXml.close()
        settingXml.write('</settings>\n');
        settingXml.close()
        
    #def getControlsUpdate(self) :
    #    for setting in settings :
    #        setting.getControl(self.window)
    
    def getXMLControl(self):
        tree = ElementTree().parse(os.path.join(BASE_RESOURCE_PATH,'settings.xml'))
        for cat in tree.findall('category'):
            for setting in cat.findall('setting') :
                if "id" in setting.keys():
                    setting_name = setting.attrib['id']
                    self.settings.append(Setting(setting_name))
        
    def getDefaults(self) :
        #get default value here
        pass
        
    
    def applyXbianUpdate(self) :
        previousCL = 0
        data = {}
        for setting in self.settings :
            if setting.isActive() :
                data[setting.getKey()] = setting.getValue()
                previousCL = setting.getControlLevel()                
                if setting.getControlLevel() == 0 :             
                    setting.updateXbian(data)
                    data = {}
    
                    
                    
    def createWindowDialogXml(self):
        dynxml = open(os.path.join(BASE_RESOURCE_PATH,'skins','Default','720p','XbianUpdateWindowDialog.dynxml'))
        realxml = open(os.path.join(BASE_RESOURCE_PATH,'skins','Default','720p','XbianUpdateWindowDialog.xml'),'w')
        
        for line in dynxml.readlines() :
            if line.find("<xbian>ControlGroup<xbian>") != -1:
                realxml.write(self.getListRadioButtonXml())
            else :
                realxml.write(line)
        dynxml.close()
        realxml.close()
        self.window = Window('XbianUpdateWindowDialog.xml',ADDON_DIR, "Default")
        self.window.onAction = self.onAction
        self.window.onClick = self.onClick
        if self.hasChanged :
            #threadModalDialog = threading.Thread(None, self.window.doModal, None, (), {'nom':'thread ModalDialog'})
            #threadModalDialog.start()
            self.window.doModal()
            for setting in self.settings :
                if setting.isActive() :
                    setting.getControl(self.window)
        
    
    def getListRadioButtonXml(self):
        xml =  '<control type="grouplist" id="59999">\n'
        xml += '<posy>100</posy>\n'
        xml += '<posx>30</posx>\n'
        xml += '<height>340</height>\n'
        xml += '<ondown>11</ondown>\n'
        xml += '<onright>10</onright>\n'
        xml += '<onleft>11</onleft>\n'
        xml += '<onup>11</onup>\n'
        changed = False
        self.settings.reverse()
        previousCL = 0
        subSettings = []
        self.hasChanged = False
        for setting in self.settings :
            print setting.getKey()
            print setting.getControlLevel()
            if setting.getControlLevel() > previousCL :
                print 'new level'
                changed = False
                previousCL = setting.getControlLevel()
            if setting.isUpdated() :
                print 'changed set to true'
                changed = True
            if changed and setting.getControlLevel() == 0 :
                print 'create button'
                xml += setting.getRadioButtonXml()
                setting.setActive(True)
                subSettings.reverse()
                for subSetting in subSettings :
                    xml += subSetting.getRadioButtonXml()
                    subSetting.setActive(True)
                subSettings = []               
                changed = False
                self.hasChanged = True
                
            elif  setting.getControlLevel() > 0:
                subSettings.append(setting)
            else :
                subSettings = []
                
        xml += '</control>\n'
        return xml


####MAIN####
settings = Settings()
if ADDON.getSetting('advancedmode') == 'true' :
    xbmc.executebuiltin('Skin.SetBool(advancedmode)')
else :
    xbmc.executebuiltin('Skin.Reset(advancedmode)')

ADDON.openSettings()
#window = Window('DialogAddonSettings.xml',ADDON_DIR, "Default")
xbmc.executebuiltin('Skin.Reset(advancedmode)')
settings.createWindowDialogXml()
shutil.copy2(os.path.join(BASE_RESOURCE_PATH,'settings_addon.xml'),os.path.join(BASE_RESOURCE_PATH,'settings.xml'))

