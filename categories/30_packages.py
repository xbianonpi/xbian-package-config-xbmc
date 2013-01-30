import os
import subprocess
import time

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
import xbmcgui,xbmc
from xbmcaddon import Addon

__addonID__      = "plugin.xbianconfig"
ADDON     = Addon( __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

dialog = xbmcgui.Dialog()

RUNNING = 'running'
STOPPED = 'stopped'
RESTART = 'Restart'
STOP = 'Stop'
START = 'Start'

class PackagesControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
   

    def onInit(self) :
        tmp = xbianConfig('packages','list')
        self.packageCatList = []        
        self.packages = {}
        for cat in tmp :
            t = cat.split(',')
            tmp_cat = {}
            tmp_cat['name'] = t[0]
            tmp_cat['available'] = int(t[1])
            tmp_cat['installed'] = int(t[2])
            self.packageCatList.append(tmp_cat)
        for packageDetails in self.packageCatList :     
            self.packages[packageDetails['name']] = {}
            self.packages[packageDetails['name']]['group'] = MultiSettingControl()
            self.packages[packageDetails['name']]['label'] = CategoryLabelControl(Tag('label',packageDetails['name'].title()))
            self.packages[packageDetails['name']]['group'].addControl(self.packages[packageDetails['name']]['label'])
            self.packages[packageDetails['name']]['list'] = []
            self.packages[packageDetails['name']]['package'] = SpinControlex(Tag('label','Package'))
            self.packages[packageDetails['name']]['group'].addControl(self.packages[packageDetails['name']]['package'])
            tmp = xbianConfig('packages','list',packageDetails['name'])            
            for packag in tmp :
                packageTmp = packag.split(',')                
                pack = Content(Tag('label',packageTmp[0]),defaultSKin=False)
                self.packages[packageDetails['name']]['package'].addContent(pack)
                package = {}
                package['group'] = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.packages[packageDetails['name']]['package'].getWrapListId(),pack.getId())))
                package['status'] = ButtonControl(Tag('label',' -Status'))
                package['status'].onClick = lambda status : status.setValue(self.onStatusClick(self.getCurrentPackage(status),status.getValue()))
                package['group'].addControl(package['status'])
                package['info'] = ButtonControl(Tag('label',' -Info'))
                package['info'].onClick = lambda info : self.onInfoClick(self.getCurrentPackage(info))
                package['group'].addControl(package['info'])
                self.packages[packageDetails['name']]['group'].addControl(package['group'])
                self.packages[packageDetails['name']]['list'].append(package)
            self.addControl(self.packages[packageDetails['name']]['group'])
       
    def getCurrentPackage(self,control) :
        for key in self.packages :
            for ctrlGroup in self.packages[key]['list'] :
                for keyctrl in ctrlGroup :
                    if ctrlGroup[keyctrl] == control :
                        return self.packages[key]['package'].getValue()
    def onStatusClick(self,package,value):
        pass
    
    def onInfoClick(self,package) :
		pass
    
    
            
        
    def setValue(self,values):
        for key in values :
            for i,package in enumerate(values[key]) :
                print 'yap %s'%str(package)
                self.packages[key]['list'][i]['status'].setValue(package['status'])
        
            
        
    def getValue(self) :
        pass
            
       

class packagesManager(Setting) :
    CONTROL = PackagesControl()
    DIALOGHEADER = "XBian packages Manager"
    ERRORTEXT = "Error"
    OKTEXT = "OK"
    APPLYTEXT = "Apply"
    
    INSTALLED = 'Installed'
    NOTINSTALLED = 'Not installed'

    def onInit(self) :   
        pass    
        self.control.onStatusClick = self.onStatus
        self.control.onInfoClick = self.onInfo
        
    def onInfo(self,package) :
		rc = xbianConfig('packages','info',package)
		if rc :			
			PackageInfo(package,rc[0].partition(' ')[2],rc[1].partition(' ')[2],rc[2].partition(' ')[2],rc[3].partition(' ')[2],rc[4].partition(' ')[2],rc[5].partition(' ')[2],rc[6].partition(' ')[2])
			
    
    def onStatus(self,package,value) :
        wait = xbmcgui.DialogProgress()
        if value == self.INSTALLED :
            self.APPLYTEXT = 'Do you want to remove the %s package?'%package
            if self.askConfirmation(True) :
                wait.create('Removing %s'%package,'Please Wait while removing...')
                wait.update(0)
                rc = xbianConfig('packages','remove',package)
                if rc and rc[0] == '1' :
                    #remove package
                    waitRemove = True
                    while waitRemove : 
                        progress = int(xbianConfig('packages','progress')[0])
                        status = int(xbianConfig('packages','status',package)[0])
                        if progress == 0 and status == 0 :
                            waitRemove = False
                        else :
                            time.sleep(0.5)
                    #refresh service list
                    self.globalMethod['Services']['refresh']()
                    wait.close()
                    self.OKTEXT = 'Package %s succesfully removed'%package
                    self.notifyOnSuccess()
                    return self.NOTINSTALLED
                elif rc and rc[0] == '2' :
                     #normally never pass here
                     wait.close()
                     self.ERRORTEXT = 'Package %s is not installed'%package
                     self.notifyOnError()
                     return self.NOTINSTALLED
                elif rc and rc[0] == '3' :
                     wait.close()
                     self.ERRORTEXT = 'Package %s is an essential package and cannot be removed'%package
                     self.notifyOnError()
                     return self.INSTALLED
                else : 
                     wait.close()
                     #normally never pass here
                     self.ERRORTEXT = 'Unknown Error while removing %s'%package
                     self.notifyOnError()
                     return self.INSTALLED
            else :
				return self.INSTALLED
        else :
            self.APPLYTEXT = 'Do you want to install the %s package?'%package
            if self.askConfirmation(True) :             
                wait.create('Installing %s'%package,'Please Wait while installing...')
                wait.update(0)
                rc = xbianConfig('packages','install',package)
                if rc and rc[0] == '1' :
                    #remove package
                    waitInstall = True
                    while waitInstall : 
                        progress = int(xbianConfig('packages','progress')[0])
                        status = int(xbianConfig('packages','status',package)[0])
                        if progress == 0 and status == 1 :
                            waitInstall = False
                        else :
                            time.sleep(0.5)
                    #refresh service list
                    self.globalMethod['Services']['refresh']()
                    wait.close()
                    self.OKTEXT = 'Package %s succesfully installed'%package
                    self.notifyOnSuccess()
                    return self.INSTALLED
                elif rc and rc[0] == '2' :
                    wait.close()
                    #normally never pass here
                    self.ERRORTEXT = 'Package %s is already installed'%package
                    self.notifyOnError()
                    return self.INSTALLED
                elif rc and rc[0] == '3' :
                    wait.close()
                    self.ERRORTEXT = 'Package %s not found in apt-repository'%package
                    self.notifyOnError()
                    return self.NOTINSTALLED
                elif rc and rc[0] == '4' :
                    wait.close() 
                    self.ERRORTEXT = 'A newer version of this package is already installed'
                    self.notifyOnError()
                    return self.INSTALLED
                elif rc and rc[0] == '5' :
                    wait.close()
                    self.ERRORTEXT = 'There is a size mismatch for the remote package'
                    self.notifyOnError()
                    return self.NOTINSTALLED
                elif rc and rc[0] == '6' :
                    wait.close()
                    self.ERRORTEXT = 'The package itself got an internal error'
                    self.notifyOnError()
                    return self.NOTINSTALLED
                else : 
                    wait.close()
                    #normally never pass here
                    self.ERRORTEXT = 'Unknown Error while installing %s'%package
                    self.notifyOnError()
                    return self.NOTINSTALLED     
            else :
				return self.NOTINSTALLED    
            
    def getXbianValue(self):
        packages = {}
        for packageCat in self.control.packageCatList :
            package = []
            tmp = xbianConfig('packages','list',packageCat['name'])
            for packag in tmp :
                packageTmp = packag.split(',')
                pack = {}
                pack['name'] = packageTmp[0]
                if packageTmp[1] == '1' :
                    pack['status'] = self.INSTALLED
                else :
                    pack['status'] = self.NOTINSTALLED
                package.append(pack)
            packages[packageCat['name']] = package
        print 'yap %s'%str(packages)
        return packages
            
        
    
    def setXbianValue(self,value):
        pass


class packages(Category) :
    TITLE = 'Packages'
    SETTINGS = [packagesManager]



