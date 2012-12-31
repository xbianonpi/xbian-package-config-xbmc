from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag

import xbmcgui

#create a Custom NetworkSetting Container Control
class NetworkSettings(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    STATIC = 'Static'
    DHCP = 'Dhcp'
    
    def onInit(self) :
        self.interfaces = {}
        self.interfaceSpinControl = SpinControlex(Tag('label','Interfaces'))
        self.addControl(self.interfaceSpinControl)
        SaveButton = ApplyButtonControl(Tag('label','Apply'))
        self.setSaveControl(SaveButton)
    
    def getClickID(self) :
		return self.save_ctrl.getId()
        
    def clickSave(self,controlId):
       if controlId == self.save_ctrl.getId() :
           value = [self.interfaceSpinControl.getValue()]
           for control in self.interfaces[self.interfaceSpinControl.getValue()].getControls() :
              if isinstance(control,ContainerXml) :
                  value.extend(control.getValue())
              else :    
                  value.append(control.getValue())
           print value
           self.onClick(self,*value)
    
    def getValue(self):
           value = [self.interfaceSpinControl.getValue()]
           for control in self.interfaces[self.interfaceSpinControl.getValue()].getControls() :
              if isinstance(control,ContainerXml) :
                  value.extend(control.getValue())
              else :    
                  value.append(control.getValue())
           return  value
        
    def setValue(self,interface,mode,status,ipadress=None,subnet=None,gateway=None,dns1=None,dns2=None,ssid=None) :
        Staticvalue = [ipadress,subnet,gateway,dns1,dns2]
        controls = self.interfaces[interface].getControls()
        controls[0].setValue(status)
        if mode=='dhcp' :
            mode = self.DHCP
        else :
            mode = self.STATIC
            
        controls[1].setValue(mode)
        #if mode == self.STATIC :
        for i,control in enumerate(controls[2].getControls()) :
            control.setValue(Staticvalue[i])          
        if ssid :
            controls[3].setValue(ssid)
       
    def addInterface(self,interface,wifi=False):
        interfaceTmp = {}
        interfaceTmp['content'] = Content(Tag('label',interface),defaultSKin=False)
        self.interfaceSpinControl.addContent(interfaceTmp['content'])
       
        lanGroup = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.interfaceSpinControl.getWrapListId(),interfaceTmp['content'].getId())))
        
        interfaceTmp['status'] = ButtonControl(Tag('label',' -Status'))
        lanGroup.addControl(interfaceTmp['status'])
        
        interfaceTmp['mode'] = SpinControlex(Tag('label',' -Mode'))
        dhcp = Content(Tag('label',self.DHCP),defaultSKin=False)
        static = Content(Tag('label',self.STATIC),defaultSKin=False)
        interfaceTmp['mode'].addContent(dhcp)
        interfaceTmp['mode'].addContent(static)
        lanGroup.addControl(interfaceTmp['mode'])

        StaticGroup = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(interfaceTmp['mode'].getWrapListId(),static.getId())))
        Adress = ButtonControl(Tag('label',' -Adress'))
        Adress.onClick = self.SetAdress
        StaticGroup.addControl(Adress)
        Subnet = ButtonControl(Tag('label',' -Subnet'))
        Subnet.onClick = self.SetSubnet
        StaticGroup.addControl(Subnet)
        Gateway = ButtonControl(Tag('label',' -Gateway'))
        Gateway.onClick = self.SetGateway
        StaticGroup.addControl(Gateway)
        DNS1 = ButtonControl(Tag('label',' -Primary Dns'))
        DNS1.onClick = self.SetDns1
        StaticGroup.addControl(DNS1)
        DNS2 = ButtonControl(Tag('label',' -Secondary Dns'))
        DNS2.onClick = self.SetDns2
        StaticGroup.addControl(DNS2)

        lanGroup.addControl(StaticGroup)

        if wifi :
            WirelessGroup = ButtonControl(Tag('label',' -Ssid'),Tag('label2','Not Connected'))
            WirelessGroup.onClick = self.SetSSID
            lanGroup.addControl(WirelessGroup)        
        self.addControl(lanGroup)
        self.interfaces[interface] = lanGroup
    
    def SetAdress(self,ctrl,value):
        ip = xbmcgui.Dialog().numeric(3,"Set Ip Adress",value)
        ctrl.setValue(ip)
            
    def SetSubnet(self,ctrl,value):
        subnet = xbmcgui.Dialog().numeric(3,"Set Subnet Mask",value)
        ctrl.setValue(subnet)
    
    def SetGateway(self,ctrl,value):
        gateway = xbmcgui.Dialog().numeric(3,"Set Gateway",value)
        ctrl.setValue(gateway)

    def SetDns1(self,ctrl,value):
        dns = xbmcgui.Dialog().numeric(3,"Set Primary Dns",value)
        ctrl.setValue(dns)

    def SetDns2(self,ctrl,value):
        dns = xbmcgui.Dialog().numeric(3,"Set Secondary Dns",value)
        ctrl.setValue(dns)

    def SetSSID(self,ctrl,value):
        dialog = xbmcgui.Dialog()
        SSID = ['tele2','bbox2','test']
        rc = dialog.select("Select Network", SSID)
        ctrl.setValue(SSID[rc])
