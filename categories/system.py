from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category

from lib.NetworkCustomControlSetting import NetworkSettings

from resources.lib.xbianconfig import xbianConfig
import xbmcgui
import os

dialog=xbmcgui.Dialog()

class system(Category) :
    TITLE = 'System'
    
    def onInit(self) :
        #NETWORK SETTINGS
        networkCatLabel =CategoryLabelControl(Tag('label','Network'))
        self.addControl(networkCatLabel)
        
        network = NetworkSettings()
        network.onClick = self.setLan
        network.getConfig = self.getLanConfig
        network.onLoad = self.setLanConfig
        self.interfaces = xbianConfig('network','list')
        self.lanConfig = {}
        print self.interfaces
        for interface in self.interfaces :
            wifi = False
            if os.path.exists("/sys/class/net/%s/wireless"%interface) :
                wifi = True
            network.addInterface(interface,wifi)
        self.addControl(network)
        
        #CONNECTIVITY SETTINGS
        ConnectivityCatLabel =CategoryLabelControl(Tag('label','Connectivity'))
        self.addControl(ConnectivityCatLabel)
        
        ForceHdmi = RadioButtonControl(Tag('label','Force Hdmi'))
        ForceHdmi.onClick = self.SetForceHdmi
        ForceHdmi.getConfig = self.getForceHdmiConfig
        ForceHdmi.onLoad = self.setForceHdmiConfig
        self.addControl(ForceHdmi)
        
        IgnoreHdmi = RadioButtonControl(Tag('label','Disable Hdmi'))
        IgnoreHdmi.onClick = self.SetDisableHdmi
        IgnoreHdmi.getConfig = self.getDisableHdmiConfig
        IgnoreHdmi.onLoad = self.setDisableHdmiConfig
        self.addControl(IgnoreHdmi)
        
        enableCec = RadioButtonControl(Tag('label','Enable Cec'))
        enableCec.onClick = self.SetenableCec
        enableCec.getConfig = self.getenableCecConfig
        enableCec.onLoad = self.setenableCecConfig
        self.addControl(enableCec)
        
        ignoreCec = RadioButtonControl(Tag('label','Ignore Cec Init'))
        ignoreCec.onClick = self.SetignoreCec
        ignoreCec.getConfig = self.getignoreCecConfig
        ignoreCec.onLoad = self.setignoreCecConfig
        self.addControl(ignoreCec)        
        #LICENSE SETTINGS
        LicenseCatLabel = CategoryLabelControl(Tag('label','License'))
        self.addControl(LicenseCatLabel)
        
        mpgLicense = ButtonControl(Tag('label','Mpeg2'))
        mpgLicense.onClick = self.SetMpgLicense
        mpgLicense.getConfig = self.getmpgLicenseConfig
        mpgLicense.onLoad = self.setmpgLicenseConfig
        self.addControl(mpgLicense)
        
        vc1License = ButtonControl(Tag('label','Vc1'))
        vc1License.onClick = self.SetVc1License
        vc1License.getConfig = self.getvc1LicenseConfig
        vc1License.onLoad = self.setvc1LicenseConfig
        self.addControl(vc1License)
        
        
    #CALLBACK FUNCTION        
    
    #NETWORK
    def setLan(self,ctrl,interface,mode,status,ipadress,subnet,gateway,dns1,dns2,ssid=None):
        if mode == NetworkSettings.DHCP :
            mode = 'dhcp'
            cmd = [mode,interface]
        else :
            mode = 'static'
            if dns2 == '' :
				dns2 = dns1
            cmd = [mode,interface,ipadress,subnet,gateway,dns1,dns2]
        self.queueCmd(ctrl,lambda: xbianConfig('network',*cmd),self.setlanCb)
        
    def setlanCb(self,ctrl,rc) :
        if rc[0] == '1' :
            self.CmdOk('Network','Network udapte OK')
            self.mpgLicense = self.newmpgLicense
        elif rc[0] == '0' :
            self.cmdError('Network',rc[1])
            self.setmpgLicenseConfig(ctrl)
        else :
            self.cmdError('Network','Unexpecting Error : %s '%rc[0])
            self.setmpgLicenseConfig(ctrl)
        
    def getLanConfig(self):
        for interface in self.interfaces :
            interface_config = xbianConfig('network','status',interface)
            self.lanConfig[interface] = []
            for config in interface_config :
                try :
                    self.lanConfig[interface].append(config.split(' ')[1])
                except :
                    self.lanConfig[interface].append(None)
        print self.lanConfig            
        #self.lanConfig = {'eth0':[NetworkSettings.DHCP,None,None,None,None,None],}        
    
    def setLanConfig(self,ctrl):
        for key in self.lanConfig :
            ctrl.setValue(key,*self.lanConfig[key])
    
    #CONNECTIVITY
    #force hdmi
    def SetForceHdmi(self,ctrl,value):
        dialog.yesno('ForceHdmi','Set Force Hdmi to %s'%str(value))
    def getForceHdmiConfig(self):
        self.ForceHdmi = True
    def setForceHdmiConfig(self,ctrl):
        ctrl.setValue(self.ForceHdmi)
        
    #disable hdmi    
    def SetDisableHdmi(self,ctrl,value):
        dialog.yesno('IgnoreHdmi','Set Disable Hdmi to %s'%str(value))
    def getDisableHdmiConfig(self):
        self.disableHdmi = False
    def setDisableHdmiConfig(self,ctrl):
        ctrl.setValue(self.disableHdmi)
    
    #enable CEC
    def SetenableCec(self,ctrl,value):
        dialog.yesno('IgnoreHdmi','Set enable CEC to %s'%str(value))
    def getenableCecConfig(self):
        self.enablecec = False
    def setenableCecConfig(self,ctrl):
        ctrl.setValue(self.enablecec)
    
    #ignore CEC
    def SetignoreCec(self,ctrl,value):
        dialog.yesno('IgnoreHdmi','Set ignore CEC to %s'%str(value))
    def getignoreCecConfig(self):
        self.ignorecec = True
    def setignoreCecConfig(self,ctrl):
        ctrl.setValue(self.ignorecec)
    
    #LICENCE
    #mpeg License
    def SetMpgLicense(self,ctrl,value):
        kb = xbmc.Keyboard(value, 'Mpeg License Key')
        kb.doModal()
        if (kb.isConfirmed()):
            self.newmpgLicense = kb.getText()
        if self.newmpgLicense!=value :
            self.queueCmd(ctrl,lambda: xbianConfig('licensempg2',self.mpgLicenseCmd,self.newmpgLicense),self.setMpgLicenseCb)
            ctrl.setValue(self.newmpgLicense)
    
    def setMpgLicenseCb(self,ctrl,rc):
        if rc[0] == '1' :
            self.CmdOk('Mpeg Licence','Mpeg Licence udapte OK')
            self.mpgLicense = self.newmpgLicense
        elif rc[0] == '0' :
            self.cmdError('Mpeg Licence','Error while updating Mpeg License')
            self.setmpgLicenseConfig(ctrl)
        else :
            self.cmdError('Mpeg Licence','Unexpecting Error while updating Mpeg License')
            self.setmpgLicenseConfig(ctrl)
    
    def getmpgLicenseConfig(self):
        licensempg =xbianConfig('licensempg2','select')
        if licensempg[0][:2] == '0x' :
            self.mpgLicenseCmd = 'update'
            self.mpgLicense = licensempg[0]
        else :
            if licensempg[0] == "" :
                self.mpgLicenseCmd = 'insert'
            else :
                self.mpgLicenseCmd = 'update'
            self.mpgLicense = '0x'                  
    
    def setmpgLicenseConfig(self,ctrl):
        ctrl.setValue(self.mpgLicense)
    
    #VC1 License
    def SetVc1License(self,ctrl,value):
        kb = xbmc.Keyboard(value, 'Vc1 License Key')
        kb.doModal()
        if (kb.isConfirmed()):
            self.newvc1License = kb.getText()
        if self.newvc1License!=value :
            self.queueCmd(ctrl,lambda: xbianConfig('licensevc1',self.vc1LicenseCmd,self.newvc1License),self.setvc1LicenseCb)
            ctrl.setValue(self.newvc1License)
            
    def setvc1LicenseCb(self,ctrl,rc):
        if rc[0] == '1' :
            self.CmdOk('Vc1 Licence','Vc1 Licence udapte OK')
            self.vc1License = self.newvc1License
        elif rc[0] == '0' :
            self.cmdError('Vc1 Licence','Error while updating Vc1 License')
            self.setvc1LicenseConfig(ctrl)
        else :
            self.cmdError('Vc1 Licence','Unexpecting Error while updating Vc1  License')
            self.setmpgLicenseConfig(ctrl)
            
    def getvc1LicenseConfig(self):
        licensevc1 =xbianConfig('licensevc1','select')
        if licensevc1[0][:2] == '0x' :
            self.vc1LicenseCmd = 'update'
            self.vc1License = licensevc1[0]
        else :
            if licensevc1[0] == "" :
                self.vc1LicenseCmd = 'insert'
            else :
                self.vc1LicenseCmd = 'update'
            self.vc1License = '0x'                  
    
    def setvc1LicenseConfig(self,ctrl):
        ctrl.setValue(self.vc1License)
