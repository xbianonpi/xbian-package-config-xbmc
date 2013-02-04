import xbmc,xbmcgui
from xbianconfig import xbianConfig
import time
import threading
import os
from xbmcaddon import Addon

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

def getNumeric(header,default=None,min=False,max=False):
    dialog = xbmcgui.Dialog() 
    cont = True
    while cont :
        rc = dialog.numeric(0,header,default)
        cont = False
        if min :
            if int(rc) < min :
                dialog.ok(header,'Value must be greater than %d'%min)
                cont = True
        if max :
            if int(rc) > max :
                dialog.ok(header,'Value must be lower than %d'%max)
                cont = True
    return rc

def getIp(header,default=None):
    dialog = xbmcgui.Dialog() 
    return dialog.numeric(3,header,default)
    
def getText(header,default="",hidden=False):
    kb = xbmc.Keyboard(default,header,hidden)
    kb.doModal()
    if (kb.isConfirmed()):
        return kb.getText()
    else :
        return None

class PackageInfo :
	def __init__(self,header,name,versionl,versionr,sized,sizei,desc,dep):
		xbmc.executebuiltin('Skin.SetString(packageheader,Info : %s)'%header)
		xbmc.executebuiltin('Skin.SetString(packagename,Name : %s)'%name)
		xbmc.executebuiltin('Skin.SetString(packageversionr,Remote version : %s)'%versionr)
		if not versionl :
			versionl = 'Not installed'
		xbmc.executebuiltin('Skin.SetString(packageversioni,Local version : %s)'%versionl)
		xbmc.executebuiltin('Skin.SetString(packagesized,Download size : %s)'%sized)
		xbmc.executebuiltin('Skin.SetString(packagesizei,Installed size : %s)'%sizei)
		xbmc.executebuiltin('Skin.SetString(packagedesc,Description : %s)'%desc)
		if not dep :
			dep = 'None'
		xbmc.executebuiltin('Skin.SetString(packagedep,Dependency : %s)'%dep.replace(',',''))
		self.dlg = xbmcgui.WindowXMLDialog('DialogPackageInfo.xml',ROOTDIR)
		self.dlg.doModal()

class dialogWait :
	#didn't work, xbmc crash when use it
	def __init__(self,header,info):
		xbmc.executebuiltin('Skin.SetString(waitheader,%s)'%header)
		xbmc.executebuiltin('Skin.SetString(waitinfo,%s)'%info)
		self.dlg = xbmcgui.WindowXMLDialog('DialogWait.xml',ROOTDIR)
	
	def show(self):
		self.dlg.show()
		
	def close(self):
		self.dlg.close()

class WaitDlg(xbmcgui.WindowXMLDialog):	
	def update(self,header='',line1='',line2='',line3='',line4=''):
		self.headerCtrl = self.getControl(1)
		self.line1Ctrl = self.getControl(2)
		self.line2Ctrl = self.getControl(3)
		self.line3Ctrl = self.getControl(4)
		self.line4Ctrl = self.getControl(5)
		if header :
			self.headerCtrl.setLabel(self.header)
		if line1 :
			self.line1Ctrl.setLabel(line1)
		if line2 :
			self.line2Ctrl.setLabel(line2)
		if line3 :
			self.line3Ctrl.setLabel(line3)
		if line4 :
			self.line4Ctrl.setLabel(line4)
	def close2() :
		self.close()
	

SSID = 0
SECURITYTYPE = 1
SECURITY = 2
SIGNAL = 3

def wifiConnect(interface):
    dialog = xbmcgui.Dialog()    
    progress = xbmcgui.DialogProgress()
    progress.create('Scanning','Scanning for wlan on %s'%interface)
    #progress.update(0) #should hide progress bar, don't work
    networklist = xbianConfig('network','scan',interface)
    networks = []
    for network in networklist :
        tmp = network.split(',')
        tmp[SSID] = tmp[SSID].replace('"','')
        networks.append(tmp)
        
    canceled = False
    
    while not canceled :
        if progress.iscanceled():
            canceled = True
        else :
            progress.close()
            displaylist = []
            for network in networks :
                name = '%s [COLOR blue](%s)[/COLOR]'%(network[SSID],network[SECURITYTYPE])
                displaylist.append(name)
            selectedNetwork = dialog.select('Select Network',displaylist)
            if selectedNetwork == -1 :
                canceled = True
            else :
                if networks[selectedNetwork][SECURITY] == 'on' :
                    key = getText('%s : Security Key'%networks[selectedNetwork][SSID])
                    if not key :
                        continue
                else :
                    key = ""
                        
                progress.create('Scanning','Connecting %s to %s'%(interface,networks[selectedNetwork][SSID]))
                rc = xbianConfig('network','credentials',interface,networks[selectedNetwork][SECURITYTYPE],networks[selectedNetwork][SSID],key)
                if rc and rc[0] == '1' :
                    rc = xbianConfig('network','restart',interface)
                    rc = '2'
                    while rc == '2' :
                        rc = xbianConfig('network','progress',interface)[0]
                        time.sleep(0.5)
                    if rc == '1' :
                        progress.close()
                        return True
                    else :
                        progress.close()
                        dialog.ok("Wireless",'%s : cannot connect to %s (%s)'%(interface,networks[selectedNetwork][SSID],rc))
                        
    return False
        
    
