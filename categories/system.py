from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from lib.NetworkCustomControlSetting import NetworkSettings

from resources.lib.xbianconfig import xbianConfig
import xbmcgui
import os

dialog=xbmcgui.Dialog()

class NewtorkLabel(Setting) :
	CONTROL = CategoryLabelControl(Tag('label','Network'))
	
class NetworkSetting(Setting) :
    CONTROL = NetworkSettings()
    DIALOGHEADER = "NETWORK SETTINGS"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"
    BADUSERENTRYTEXT = "Your input is not Correct"
    
    def onInit(self):
        self.interfaces = xbianConfig('network','list')
        self.lanConfig = {}
        for interface in self.interfaces :
            wifi = False
            if os.path.exists("/sys/class/net/%s/wireless"%interface) :
                wifi = True
            self.getControl().addInterface(interface,wifi)
    
    def setControlValue(self,value):
        for key in value :
            self.getControl().setValue(key,*value[key])
    
    def getUserValue(self):
        return self.getControl().getValue()
    
    def getXbianValue(self):
        for interface in self.interfaces :
            interface_config = xbianConfig('network','status',interface)
            self.lanConfig[interface] = []
            for config in interface_config :
                try :
                    self.lanConfig[interface].append(config.split(' ')[1])
                except :
                    self.lanConfig[interface].append(None)
        return self.lanConfig            
    
    def setXbianValue(self,value):
        #interface,status,mode,ipadress,subnet,gateway,dns1,dns2,ssid=None
        print value
        if value[2] == NetworkSettings.DHCP :
            mode = 'dhcp'
            cmd = [mode,value[0]]
        else :
            mode = 'static'
            if value[7] == '' :
                value[7] = value[6]
            cmd = [mode,value[0],value[3],value[4],value[5],value[6],value[7]]
        rc = xbianConfig('network',*cmd)
        ok = True
        if not rc :
            ok = False
            self.ERRORTEXT = "No return Code From Xbian"
        elif rc[0] != '1' : 
            ok = False
            self.ERRORTEXT = rc[1]
        return ok           
        
        
class LicenceLabel(Setting) :
	CONTROL = CategoryLabelControl(Tag('label','License'))

class mpeg2License(Setting) :
    CONTROL = ButtonControl(Tag('label','Mpeg2'))
    DIALOGHEADER = "MPEG2 License"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    BADUSERENTRYTEXT = "Format is not Correct,must be 0x00000000"
    
    def onInit(self) :
        self.xbiankey = 'licensempg2'
        
    def getUserValue(self):
        kb = xbmc.Keyboard(self.getControlValue(),self.DIALOGHEADER)
        kb.doModal()
        if (kb.isConfirmed()):
            return kb.getText()
        else :
            return None
    
    def checkUserValue(self,value):
        try :
            hexvalue = int(value,16)
            keyok = len(value) == 10 and value[:2] == '0x'
        except :
            keyok = False   
        return keyok
    
    def getXbianValue(self):
        licenseValue =xbianConfig(self.xbiankey,'select')
        if licenseValue and licenseValue[0][:2] == '0x' :
            self.XbianLicenseCmd = 'update'
            return licenseValue[0]
        else :
            if len(licenseValue) == 0 or licenseValue[0] == "" :
                self.XbianLicenseCmd = 'insert'
            else :
                self.XbianLicenseCmd = 'update'
            return '0x'                  
    
    	
    def setXbianValue(self,value):
        rc = xbianConfig(self.xbiankey,self.XbianLicenseCmd,value)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       
        
    
class vc1License(mpeg2License) :
    CONTROL = ButtonControl(Tag('label','Vc1'))
    DIALOGHEADER = "MPEG2 License"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    BADUSERENTRYTEXT = "Format is not Correct,must be 0x00000000"
    
    def onInit(self) :
        self.xbiankey = 'licensevc1'
    
    
#CATEGORY CLASS
class system(Category) :
    TITLE = 'System'
    SETTINGS = [NewtorkLabel,NetworkSetting,LicenceLabel,mpeg2License,vc1License]
