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

# xbmc modules
import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon

 
ADDON     = Addon( __addonID__ )
Language  = ADDON.getLocalizedString
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString


ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )

MESSAGE_ACTION_OK = 11
MESSAGE_EXIT = 10
MESSAGE_TITLE = 101
MESSAGE_LINE1 = 102
MESSAGE_LINE2 = 103
MESSAGE_LINE3 = 104

SETTINGS = ('overclock','hostname','timezone','rootpw','xbianpw','wlan','lan','adress','subnet','gateway','dns1','dns2','rootlogin','forcehdmi','ignorehdmi','cecinit','cec','overscan','vc1','mpeg2')

class Window(xbmcgui.WindowXML):
	pass
	
class Setting():
    id_generator = itertools.count(60000)
    def __init__(self,key):
        self.id = next(self.id_generator)
        self.control = None
        self.key = key
        self.value = ADDON.getSetting(self.key)
    
    def isUpdated(self) :
        return self.value != ADDON.getSetting(self.key)
    
    def update(self) :
        self.value = ADDON.getSetting(self.key)
    
    def updateXbian(self) :
        #call xbian dispatcher function
        return True
        
    def getControl(self,xmlDialogWindow) :
        print xmlDialogWindow
        self.control = xmlDialogWindow.getControl(self.id)
    
    def isEnabled(self) :
        if self.control :
            return self.control.isEnabled()
        return False
        
    def getValue(self) :
        return self.value
    
    def getKey(self) :
        return self.key
    
    def getRadioButtonXml(self):
        xml =  '<control type="radiobutton" id="%d">\n'%self.id
        xml += '<description>update confirmation : %s</description>\n'%self.key
        xml += '<width>550</width>\n'
        xml += '<height>30</height>\n'
        xml += '<aligny>center</aligny>\n'
        xml += '<font>font12_title</font>\n'
        xml += '<label>Change %s to %s</label>\n'%(self.key,self.value)
        xml += '</control>\n'
        return xml

class Settings() :
    def __init__(self) :
        self.settings = []
        #read default settings here 
        self.getDefaults()
        
    def getControlsUpdate(self) :
        for setting in settings :
            setting.getControl(self.window)
    
    def getDefaults(self) :
        for setting in SETTINGS :
            self.settings.append(Setting(setting))
    
    def applyXbianUpdate(self) :
        for setting in self.settings :
            if setting.isUpdated() and setting.isEnabled() :
                #check if enable.
                setting.updateXbian()  
    
    def createWindowDialogXml(self):
        dynxml = open ('/home/belese/.xbmc/addons/plugin.program.xbian/resources/skins/Default/720p/XbianUpdateWindowDialog.dynxml')
        realxml = open ('/home/belese/.xbmc/addons/plugin.program.xbian/resources/skins/Default/720p/XbianUpdateWindowDialog.xml','w')
        
        for line in dynxml.readlines() :
            if line.find("<xbian>ControlGroup<xbian>") != -1:
                realxml.write(self.getListRadioButtonXml())
            else :
                realxml.write(line)
        dynxml.close()
        realxml.close()
        self.window = Window('XbianUpdateWindowDialog.xml',ADDON_DIR, "Default")
        self.window.doModal()
        for setting in self.settings :
            setting.getControl(self.window)
        
    
    def getListRadioButtonXml(self):
        xml =  '<control type="grouplist" id="59999">\n'
        xml += '<posy>90</posy>\n'
        xml += '<posx>30</posx>\n'
        xml += '<height>350</height>\n'
        xml += '<ondown>11</ondown>\n'
        xml += '<onright>10</onright>\n'
        xml += '<onleft>11</onleft>\n'
        xml += '<onup>11</onup>\n'
        for setting in self.settings :
            if setting.isUpdated() :
                xml += setting.getRadioButtonXml()
        xml += '</control>\n'
        return xml

xbmc.executebuiltin('Skin.Reset(advancedmode)')
settings = Settings()
#get xbian state
ADDON.openSettings()
dialog = xbmcgui.Dialog()
settings.createWindowDialogXml()
