from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext


import xbmcgui
import base64

import pickle

dialog=xbmcgui.Dialog()

class NewtorkLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.network.name')))
    
class NetworkControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    DHCP = 'DHCP'
    STATIC = 'Static'
    
    def onInit(self) :
        self.interface = SpinControlex(Tag('label',_('xbian-config.network.interfaces.select')))
        self.addControl(self.interface)
        self.interfacelist = xbianConfig('network','list')
        self.interfaceValue = {}        
        
        for interface in self.interfacelist :
             self.interfaceValue[interface] = {}
             self.interfaceValue[interface]['content'] = Content(Tag('label',interface),defaultSKin=False)
             self.interface.addContent(self.interfaceValue[interface]['content'])
             
             #create the interface group             
             self.interfaceValue[interface]['group'] = MultiSettingControl(Tag('visible','StringCompare(Skin.String(%s),%s)'%(self.interface.getKey(),interface)))
             #self.interfaceValue[interface]['group'] = MultiSettingControl()
             self.addControl(self.interfaceValue[interface]['group'])
             
             #add status control
             self.interfaceValue[interface]['status'] = ButtonControl(Tag('label',' -%s'%_('xbian-config.network.label.status')))
             self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['status'])
             
             #check if Wifi
             self.interfaceValue[interface]['wifi'] = False
             if xbianConfig('network','type',interface)[0] == '1':
                 self.interfaceValue[interface]['wifi'] = True
                 self.interfaceValue[interface]['ssid'] = ButtonControl(Tag('label',' -%s'%_('xbian-config.network.label.ssid')))
                 self.interfaceValue[interface]['ssid'].onClick = lambda wifi : self.wifi(interface) 
                 self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['ssid'])
                 
             
             #add interface mode Control (static/dhcp)
             self.interfaceValue[interface]['mode'] = SpinControlex(Tag('label',' -%s'%_('xbian-config.network.label.type')))
             dhcp = Content(Tag('label',self.DHCP),defaultSKin=False)
             static = Content(Tag('label',self.STATIC),defaultSKin=False)
             self.interfaceValue[interface]['mode'].addContent(dhcp)
             self.interfaceValue[interface]['mode'].addContent(static)
             self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['mode'])
             
             #add Static Group
             self.interfaceValue[interface]['staticgroup'] = MultiSettingControl(Tag('visible','StringCompare(Skin.String(%s),%s)'%(self.interfaceValue[interface]['mode'].getKey(),self.STATIC)))
             #self.interfaceValue[interface]['staticgroup'] = MultiSettingControl()
             self.interfaceValue[interface]['ipadress'] = ButtonControl(Tag('label','  -%s'%_('xbian-config.network.label.ipaddress')))
             self.interfaceValue[interface]['ipadress'].onClick = lambda ipadress: ipadress.setValue(getIp(_('xbian-config.network.label.ipaddress'),ipadress.getValue()))
             self.interfaceValue[interface]['subnet'] = ButtonControl(Tag('label','  -%s'%_('xbian-config.network.label.netmask')))
             self.interfaceValue[interface]['subnet'].onClick = lambda subnet: subnet.setValue(getIp(_('xbian-config.network.label.netmask'),subnet.getValue()))
             self.interfaceValue[interface]['gateway'] = ButtonControl(Tag('label','  -%s'%_('xbian-config.network.label.gateway')))
             self.interfaceValue[interface]['gateway'].onClick = lambda gateway: gateway.setValue(getIp(_('xbian-config.network.label.gateway'),gateway.getValue()))
             self.interfaceValue[interface]['dns1'] = ButtonControl(Tag('label','  -%s 1'%_('xbian-config.network.label.nameserver')))
             self.interfaceValue[interface]['dns1'].onClick = lambda dns1: dns1.setValue(getIp('-%s 1'%_('xbian-config.network.label.nameserver'),dns1.getValue()))
             self.interfaceValue[interface]['dns2'] = ButtonControl(Tag('label','  -%s 2'%_('xbian-config.network.label.nameserver')))
             self.interfaceValue[interface]['dns2'].onClick = lambda dns2: dns2.setValue(getIp('-%s 2'%_('xbian-config.network.label.nameserver'),dns2.getValue()))
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['ipadress'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['subnet'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['gateway'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['dns1'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['dns2'])
             self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['staticgroup'])
             
                
    def setValue(self,values):        
        default = values[0]
        self.interface.setValue(default)
        networkValue = values[1]        
        for key in networkValue :            
            value = networkValue[key]                        
            if value[0] == 'static' :
                self.interfaceValue[key]['mode'].setValue(self.STATIC)
            else:
                self.interfaceValue[key]['mode'].setValue(self.DHCP)
         
            self.interfaceValue[key]['status'].setValue(value[1])    
            self.interfaceValue[key]['ipadress'].setValue(value[2])            
            self.interfaceValue[key]['subnet'].setValue(value[3])
            self.interfaceValue[key]['gateway'].setValue(value[4])
            self.interfaceValue[key]['dns1'].setValue(value[5])            
            self.interfaceValue[key]['dns2'].setValue(value[6])
            
            if self.interfaceValue[key]['wifi'] :
                self.interfaceValue[key]['ssid'].setValue('%s'%value[7]) 
               
   
    def wifi(self,interface) :
        pass
        
    def getValue(self) :
       default = self.interface.getValue()
       networkValue = {}
       for interface in self.interfacelist :           
           networktmp = self.interfaceValue[interface]['group'].getValue()
           #sort to be compliant to xbianconfig
           networkValue[interface] = []           
           if self.interfaceValue[interface]['wifi'] :
               networkValue[interface].append(networktmp[2].lower())
               networkValue[interface].append(networktmp[0])
               networkValue[interface].append(networktmp[3])
               networkValue[interface].append(networktmp[4])
               networkValue[interface].append(networktmp[5])
               networkValue[interface].append(networktmp[6])
               networkValue[interface].append(networktmp[7])
               networkValue[interface].append(networktmp[1])
           else :
               networkValue[interface].append(networktmp[1].lower())
               networkValue[interface].append(networktmp[0])
               networkValue[interface].append(networktmp[2])
               networkValue[interface].append(networktmp[3])
               networkValue[interface].append(networktmp[4])
               networkValue[interface].append(networktmp[5])
               networkValue[interface].append(networktmp[6])
       return [default,networkValue]
        
class NetworkSetting(Setting) :
    CONTROL = NetworkControl()    
    DIALOGHEADER = _('xbian-config.network.label.name')
    ERRORTEXT = _('xbian-config.dialog.error')
    OKTEXT = _('xbian-config.dialog.ok')
    SAVEMODE = Setting.ONUNFOCUS
    
    def onInit(self) :
        self.control.wifi = self.connectWifi
        
    def connectWifi(self,interface) :
        self.userValue = self.getUserValue()
        if self.isModified() :
            progress = dialogWait(_('xbian-config.updates.update.running'),_('xbian-config.network.label.reloading_values')%(interface))
            progress.show()              
            self.setXbianValue(self.userValue)
            progress.close()
            
        if wifiConnect(interface) :
            progress = dialogWait('Refresh',_('xbian-config.network.label.reloading_values')%(interface))
            progress.show()              
            interface_config = xbianConfig('network','status',interface)
            
            lanConfig = []
            values = dict(map(lambda x : x.split(' '),interface_config))                        
            guivalues = ['mode','state','ip','netmask','gateway','nameserver1','nameserver2','ssid']
            
            for val in guivalues :
                value = None
                if val == 'mode' and values['mode'] == 'manual':
                    value = 'static'
                elif val == 'mode':
                    value = values.get('mode')
                elif val == 'ssid':
                    value = values.get('ssid')
                    if not value :
                        value = 'Not connected'
                    else :
						value = base64.b64decode(value)               
                else :
                    value = values.get(val)
                lanConfig.append(value)                                                
            self.xbianValue[interface] = lanConfig 
            progress.close()            
            self.setControlValue({interface : lanConfig})
            self.OKTEXT = _('xbian-config.network.connection.success')%interface
            self.notifyOnSuccess()
        else :
            self.ERRORTEXT = _('xbian-config.network.connection.failed')%interface
            self.notifyOnError()    
        
    def setControlValue(self,value) :
        self.control.setValue([self.default,value])
    
    def isModified(self) :
        equal = False
        for key in self.userValue :
            if self.xbianValue[key][0] != self.userValue[key][0] :
                equal = True
                break
            if self.userValue[key][0] != 'dhcp' :
                j = (0,2,3,4,5,6)
                for i in j :
                    if self.xbianValue[key][i] != self.userValue[key][i] :
                        equal = True
                        break
        return equal 
    
    def getUserValue(self):
        tmp = self.getControl().getValue()
        self.default = tmp[0]
        return tmp[1]
    
    def getXbianValue(self):
        self.default = False
        self.lanConfig={}
        for interface in self.getControl().interfacelist :
            interface_config = xbianConfig('network','status',interface)
            if interface_config[2] == 'UP' or not self.default :
                self.default = interface
            self.lanConfig[interface] = []            
                        
            values = dict(map(lambda x : x.split(' '),interface_config))                        
            guivalues = ['mode','state','ip','netmask','gateway','nameserver1','nameserver2','ssid']
            for val in guivalues :
                value = None
                if val == 'mode' and values['mode'] == 'manual':
                    value = 'static'
                elif val == 'mode':
                    value = values.get('mode')
                elif val == 'ssid':
                    value = values.get('ssid')
                    if not value :
                        value = 'Not connected'
                    else :
						value = base64.b64decode(value)               
                else :
                    value = values.get(val)
                self.lanConfig[interface].append(value)            
        return self.lanConfig
    
    def setXbianValue(self,values):
        ok = True
        for interface in values :
            if values[interface] != self.xbianValue[interface]:
                if values[interface][0].lower() == NetworkControl.DHCP.lower() :
                    mode = 'dhcp'
                    cmd = [mode,interface]
                else :
                     mode = 'static'
                     cmd = [mode,interface,values[interface][2],values[interface][3],values[interface][4],values[interface][5],values[interface][6]]
                rc = xbianConfig('network',*cmd)                
                if not rc :
                    ok = False
                    self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
                elif rc[0] != '1' : 
                    ok = False
                    try :
                        self.ERRORTEXT = rc[1]
                    except :
                        self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
        return ok           
        
        
class LicenceLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.licenses.name')))

class mpeg2License(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.licensempg2.name')))
    DIALOGHEADER = _('xbian-config.licensempg2.name')    
    OKTEXT = _('xbian-config.license.updated')%_('xbian-config.licensempg2.name')
    BADUSERENTRYTEXT = _('xbian-config.license.invalid')%_('xbian-config.licensempg2.name')
    
    def onInit(self) :
        self.xbiankey = 'licensempg2'
        
    def getUserValue(self):
        return getText(self.DIALOGHEADER,self.getControlValue())
        
    def checkUserValue(self,value):
        try :
            hexvalue = int(value,16)
            keyok = ((len(value) == 10) or (len(value) == 9))  and value[:2] == '0x'
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
    CONTROL = ButtonControl(Tag('label',_('xbian-config.licensevc1.name')))
    DIALOGHEADER = _('xbian-config.licensevc1.name')    
    OKTEXT = _('xbian-config.license.updated')%_('xbian-config.licensevc1.name')
    BADUSERENTRYTEXT = _('xbian-config.license.invalid')%_('xbian-config.licensevc1.name')
    
    def onInit(self) :
        self.xbiankey = 'licensevc1'
    
class connectivityLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.connectivity.name')),ADVANCED)

class videooutputControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    
    def onInit(self) :
        self.videooutputlist = xbianConfig('videoflags','list',cache=True)
        self.videooutputcontrol = {}
        for videooutput in self.videooutputlist :            
            self.videooutputcontrol[videooutput] = RadioButtonControl(Tag('label',_('xbian-config.videoflags.%s'%videooutput)))
            self.videooutputcontrol[videooutput].onClick = lambda forwardclick : self.onClick(self)
            self.addControl(self.videooutputcontrol[videooutput])
        
    def setValue(self,values) :
        for key in values :
            if values[key] == '1' :
                boolvalue = True
            else :
                boolvalue = False
            self.videooutputcontrol[key].setValue(boolvalue)
            
    def getValue(self) :
        rc = {}
        for videooutput in self.videooutputlist :
            rc[videooutput] = str(self.videooutputcontrol[videooutput].getValue())
        return rc
            
            
            

class videooutput(Setting) :
    CONTROL = videooutputControl(ADVANCED)
    DIALOGHEADER = _('xbian-config.connectivity.name')
                    
    def onInit(self) :
        #self.listvalue = xbianConfig('videoflags','list')
        self.listvalue = self.control.videooutputlist
        self.value = {}
        
    def getUserValue(self):
        return self.getControlValue()
    
    def getXbianValue(self):
        for value in self.listvalue :
            if not self.value.has_key(value) :
                self.value[value] = xbianConfig('videoflags','select',value)[0]
        return self.value
        
    def setXbianValue(self,value):
        #set xbian config here
        for key in value :
            if value[key] != self.xbianValue[key] :
                 rc = xbianConfig('videoflags','update',key,value[key])
                 self.DIALOGHEADER = _('xbian-config.videoflags.%s'%key)
                 break
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class SytemLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.system.name')),ADVANCED)
            
    
class hostname(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.hostname.name')),ADVANCED)
    DIALOGHEADER = _('xbian-config.hostname.name')    
    OKTEXT = _('xbian-config.hostname.changed')
    #BADUSERENTRYTEXT = "You used invalid characters in the new hostname"
        
    def getUserValue(self):
        return getText(self.DIALOGHEADER,self.getControlValue())
        
    def checkUserValue(self,value):
        return value.isalnum()
    
    def getXbianValue(self):
        licenseValue =xbianConfig('hostname','select')
        if licenseValue :
            return licenseValue[0]
        else :
            return ''                
        
    def setXbianValue(self,value):
        rc = xbianConfig('hostname','update',value)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       

class kernel(Setting) :
    CONTROL = SpinControlex(Tag('label',_('xbian-config.kernel.name')),ADVANCED)
    DIALOGHEADER = '%s %s'%(_('xbian-config.kernel.name'),_('xbian-config.kernel.label.version'))  
    OKTEXT = _('xbian-config.kernel.switch_success')
    SAVEMODE = Setting.ONUNFOCUS
    
    def onInit(self):
        kernellist =xbianConfig('kernel','list')
        for kernel in kernellist :
            content = Content(Tag('label',kernel),defaultSKin=False)
            self.control.addContent(content)

    def getUserValue(self):
        return self.control.getValue()
        
    def getXbianValue(self):
        kernelVersion =xbianConfig('kernel','select')
        if kernelVersion :
            return kernelVersion[0]
        else :
            return ''                
        
    def setXbianValue(self,value):
        rc = xbianConfig('kernel','update',value)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            if rc[0] in ('-1','-3') :
                self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
            elif rc[0] == '-2' :
                self.ERRORTEXT = _('xbian-config.kernel.same_version')            
            ok = False
        return ok

class OverclockControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    
    def onInit(self) :
        self.overclockMode = SpinControlex(Tag('label',_('xbian-config.overclocking.name')))
        self.addControl(self.overclockMode)
        self.overclockinglist = xbianConfig('overclocking','list',cache=True)

        for mode in self.overclockinglist :
             content = Content(Tag('label',mode),defaultSKin=False)
             self.overclockMode.addContent(content)
             if mode == 'Custom' :
                 self.customOverclock = MultiSettingControl(Tag('visible','StringCompare(Skin.String(%s),%s)'%(self.overclockMode.getKey(),mode)))
                 self.Arm = ButtonControl(Tag('label',' -Arm'))
                 self.Core = ButtonControl(Tag('label',' -Core'))
                 self.Sdram = ButtonControl(Tag('label',' -SDram'))
                 self.Overvoltage = ButtonControl(Tag('label',' -Overvoltage'))
                 self.customOverclock.addControl(self.Arm)
                 self.customOverclock.addControl(self.Core)
                 self.customOverclock.addControl(self.Sdram)
                 self.customOverclock.addControl(self.Overvoltage)
                 self.addControl(self.customOverclock)
    
    def setValue(self,value):
        if value :            
            #trick to get list in lower case
            for val in self.overclockinglist :
                if value[0] == val.lower() :
                    break
            self.overclockMode.setValue(val)
            self.Arm.setValue(value[1])
            self.Arm.onClick = lambda arm: self.Arm.setValue(getNumeric('Arm Overclocking',value[1],400,1200))
            self.Core.setValue(value[2])    
            self.Core.onClick = lambda core: self.Core.setValue(getNumeric('Arm Overclocking',value[2],100,600))
            self.Sdram.setValue(value[3])
            self.Sdram.onClick = lambda sdram: self.Sdram.setValue(getNumeric('Arm Overclocking',value[3],100,600))
            self.Overvoltage.setValue(value[4])
            self.Overvoltage.onClick = lambda overvolt: self.Overvoltage.setValue(getNumeric('Arm Overclocking',value[4],0,12))

class overclocking(Setting) :
    CONTROL = OverclockControl(ADVANCED)
    DIALOGHEADER = _('xbian-config.overclocking.name')    
    OKTEXT = _('xbian-config.overclocking.changed')
    SAVEMODE = Setting.ONUNFOCUS
            
    def getUserValue(self):
        values =  self.control.getValue()
        if values :
            values[0] = values[0].lower()
        return values
        
    def getXbianValue(self):
        overclock =xbianConfig('overclocking','select')
        value = xbianConfig('overclocking','values')       
        if overclock and value:
            overclock.extend(value[0].split(' '))          
            return overclock
        else :
            return []                
        
    def setXbianValue(self,value):
        if value[0] != 'custom' :
            val = [value[0]]
        else :
            val = value
        
        rc = xbianConfig('overclocking','update',*val)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            if rc[0] == '-1' :
                self.ERRORTEXT = "preset doesn't exist"
            elif rc[0] == '-2' :
                self.ERRORTEXT = 'invalid number of arguments'
            elif rc[0] == '-3' :
                self.ERRORTEXT = "non-numeric arguments"
            ok = False
        return ok


class timezone(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.timezone.name')),ADVANCED)
    DIALOGHEADER = _('xbian-config.timezone.name')    
    
    def setControlValue(self,value) :
        self.control.setValue('%s / %s'%(value[0].title(),value[1].title()))
            
    def getUserValue(self):
        continentList = xbianConfig('timezone','list')
        continentgui = []
        have_to_stop = False
        while not have_to_stop :
            for continent in continentList :
                continentgui.append(continent.replace('_',' ').title())
            rcr = dialog.select(_('xbian-config.timezone.label.timezone'),continentgui)
            if rcr == -1 :
                have_to_stop = True
            else :
                countrylist = xbianConfig('timezone','list',continentList[rcr])
                countrygui = []
                for country in countrylist :
                    countrygui.append(country.replace('_',' ').title())
                rcc = dialog.select(_('xbian-config.timezone.label.location'),countrygui)
                if rcc != -1 :
                   return [continentList[rcr],countrylist[rcc]]
        return self.xbianValue
        
    def getXbianValue(self):
        timezone =xbianConfig('timezone','select')
        if timezone and timezone[0] != '-1':
            return(timezone[0].split(' '))          
        else :
            return [_('xbian-config.timezone.notset'),_('xbian-config.timezone.notset')]                
        
    def setXbianValue(self,value):
        rc = xbianConfig('timezone','update',*value)
        ok = True
        if not rc or not rc[0]: 
            ok = False
        return ok

class AccountLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.accounts.name')),ADVANCED)
    
    def onInit(self):
        #check if advanced mode is set
        #must check here and not in preference since value are read one by one when plugin start.
        #and this setting is read before preference - advanced mode
        key = 'advancedmode'
        rc = self.getSetting(key)
        if rc == '1' :
            setvisiblecondition(key,True)            
        else :
            setvisiblecondition(key,False)
    
class rootpwd(Setting) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.rootpass.name')),ADVANCED)
    DIALOGHEADER = _('xbian-config.rootpass.label.password')        
    OKTEXT = _('xbian-config.rootpass.changed')
    BADUSERENTRYTEXT = _('xbian-config.rootpass.no_match')
        
    def onInit(self):
        self.forceUpdate = True
        self.password = None
        self.key = 'rootpass'
        
    def checkUserValue(self,value):
        return self.password == self.confirmpwd
    def getUserValue(self):
        self.password = getText(self.DIALOGHEADER,hidden=True)
        self.confirmpwd = getText(self.DIALOGHEADER,hidden=True)
        return '*****'
        
    def getXbianValue(self):
        return '*****'                
        
    def setXbianValue(self,value):
        rc = xbianConfig(self.key,'update',self.password)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       

class xbianpwd(rootpwd) :
    CONTROL = ButtonControl(Tag('label',_('xbian-config.xbianpass.name')),ADVANCED)
    OKTEXT = _('xbian-config.xbianpass.changed')
    
    def onInit(self):
        self.forceUpdate = True
        self.password = None
        self.key = 'xbianpass'
    
class sshroot(Setting) :
    CONTROL = RadioButtonControl(Tag('label',_('xbian-config.sshroot.name')),ADVANCED)
    DIALOGHEADER = _('xbian-config.sshroot.name')
                    
    def getUserValue(self):
        return str(self.getControlValue())
    
    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)
    
    def getXbianValue(self):
        rc = xbianConfig('sshroot','status')
        return rc[0]
        
    def setXbianValue(self,value):
        if value == '1':
            cmd = 'enable'
        else :
            cmd = 'disable'
        rc = xbianConfig('sshroot',cmd)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       

#CATEGORY CLASS
class system(Category) :
    TITLE = _('xbian-config.system.name')
    SETTINGS = [NewtorkLabel,NetworkSetting,LicenceLabel,mpeg2License,vc1License,SytemLabel,hostname,timezone,kernel,overclocking,AccountLabel,rootpwd,xbianpwd,sshroot,connectivityLabel,videooutput]
    
