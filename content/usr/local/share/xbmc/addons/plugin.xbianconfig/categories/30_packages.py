import uuid
import os
import time

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext


import xbmcgui,xbmc
from xbmcaddon import Addon

#apt log file (will be displayed in backgroung progress)
APTLOGFILE = '/tmp/aptstatus'

#XBMC SKIN VAR
#apt running lock
SKINVARAPTRUNNIG = 'aptrunning'

#HELPER CLASS
class PackageCategory :
    def __init__(self,packagesInfo,onPackageCB,onGetMoreCB) :
        tmp = packagesInfo.split(',')
        self.name = tmp[0]
        xbmc.log('XBian-config : initalisie new package category : %s'%self.name,xbmc.LOGDEBUG)
        self.available = int(tmp[1])
        self.preinstalled = int(tmp[2])
        self.onPackageCB = onPackageCB
        self.onGetMoreCB = onGetMoreCB
        self.installed = 0
        self.initialiseIndex = 0
        self.flagRemove = False
        self.packageList = []
        self.control = MultiSettingControl()
        self._createControl()
        self.getMoreState = False


    def hasInstalledPackage(self) :
        xbmc.log('XBian-config : %s hasInstalledPackage '%(self.name),xbmc.LOGDEBUG)
        print self.preinstalled
        return self.preinstalled > 0

    def getName(self) :
        return self.name

    def getAvailable(self) :
        return self.available

    def getInstalled(self) :
        return self.installed

    def addPackage(self,package) :
        xbmc.log('XBian-config : Add package %s to category %s'%(package,self.name),xbmc.LOGDEBUG)
        idx = self.initialiseIndex
        find = False
        if self.flagRemove :
            for i,pack in enumerate(self.packageList) :
               if pack.getName() == package :
                   find = True
                   break
            if find :
                idx = i

        if not find : self.initialiseIndex += 1

        self.packageList[idx].enable(package)
        self.installed += 1
        self.LabelPackageControl.setLabel('%s [COLOR lightblue](%d/%d)[/COLOR]'%(self.name,self.installed,self.available))
        if self.installed == self.available :
            #hide get more button
            xbmc.executebuiltin('Skin.Reset(%s)'%self.visiblegetmorekey)
            self.getMoreState = False
        elif not self.getMoreState :
            #as we can't call during progress (xbmc bug), nasty workaround and set here
            xbmc.executebuiltin('Skin.SetBool(%s)'%self.visiblegetmorekey)
            self.getMoreState = True

    def removePackage(self,package) :
        xbmc.log('XBian-config : Remove package %s from category %s'%(package,self.name),xbmc.LOGDEBUG)
        filter(lambda x : x.getName() == package,self.packageList[:self.initialiseIndex])[0].disable()       
        self.flagRemove = True
        self.installed -= 1
        #refresh category label
        self.LabelPackageControl.setLabel('%s [COLOR lightblue](%d/%d)[/COLOR]'%(self.name,self.installed,self.available))
        if not self.getMoreState :
            self.enableGetMore()

    def getControl(self) :
        return self.control

    def enableGetMore(self) :
        xbmc.executebuiltin('Skin.SetBool(%s)'%self.visiblegetmorekey)
        self.getMoreState = True

    def clean(self) :
        #clean xbmc skin var
        xbmc.executebuiltin('Skin.Reset(%s)'%self.visiblegetmorekey)
        map(lambda x : x.clean(),self.packageList)

    def _createControl(self) :
        self.LabelPackageControl = CategoryLabelControl(Tag('label','%s [COLOR lightblue](%d/%d)[/COLOR]'%(self.name,self.preinstalled,self.available)))
        self.control.addControl(self.LabelPackageControl)
        for i in xrange(self.available) :
            self.packageList.append(Package(self._onPackageCLick))
            self.control.addControl(self.packageList[-1].getControl())
        self.visiblegetmorekey = uuid.uuid4()
        self.getMoreControl = ButtonControl(Tag('label',_('xbian-config.packages.label.get_more')),Tag('visible','skin.hasSetting(%s)'%self.visiblegetmorekey),Tag('enable','!skin.hasSetting(%s)'%SKINVARAPTRUNNIG))
        self.getMoreControl.onClick = self._ongetMoreClick
        self.control.addControl(self.getMoreControl)

    def _ongetMoreClick(self,ctrl) :
        self.onGetMoreCB(self.name)

    def _onPackageCLick(self,package):
        xbmc.log('XBian-config : on PackageGroupCLickCB %s click package %s: '%(self.name,package),xbmc.LOGDEBUG)
        self.onPackageCB(self.name,package)

class Package :
    def __init__(self,onPackageCB) :
        self.onPackageCB = onPackageCB
        self.visiblekey = uuid.uuid4()
        self.label = 'Not Loaded'
        self.control = ButtonControl(Tag('label',self.label),Tag('visible','skin.hasSetting(%s)'%self.visiblekey),Tag('enable','!skin.hasSetting(%s)'%SKINVARAPTRUNNIG))
        self.control.onClick = self._onClick

    def getName(self) :
        return self.label

    def disable(self) :
        xbmc.log('XBian-config : Disable package %s'%self.label,xbmc.LOGDEBUG)
        xbmc.executebuiltin('Skin.Reset(%s)'%self.visiblekey)
        self.control.setLabel('')

    def enable(self,package) :
        xbmc.log('XBian-config : Enable package %s'%package,xbmc.LOGDEBUG)
        self.label = package
        self.control.setLabel(self.label)
        self.control.setEnabled(True)
        xbmc.executebuiltin('Skin.SetBool(%s)'%self.visiblekey)

    def getControl(self) :
        return self.control

    def clean(self) :
        xbmc.executebuiltin('Skin.Reset(%s)'%self.visiblekey)

    def _onClick(self,ctrl) :
        xbmc.log('XBian-config : on Package %s click '%self.label,xbmc.LOGDEBUG)
        self.onPackageCB(self.label)

#XBIAN GUI CONTROL
class PackagesControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self) :
        self.packages = []
        self.onGetMore=None
        self.onPackage=None
        packagelist = xbianConfig('packages','list')
        if packagelist[0] == '-3':
			xbianConfig('packages','updatedb')
			packagelist = xbianConfig('packages','list')
        for package in packagelist :
            self.packages.append(PackageCategory(package,self._onPackage,self._onGetMore))
            self.addControl(self.packages[-1].getControl())

    def setCallback(self,onGetMore=None,onPackage=None):
       self.onGetMore=onGetMore
       self.onPackage=onPackage
    
    def addPackage(self,group,package) :
		filter(lambda x : x.getName() == group,self.packages)[0].addPackage(package)

    def removePackage(self,group,package) :
		a =filter(lambda x : x.getName() == group,self.packages)
		print a
		a[0].removePackage(package)
    
    def _onPackage(self,package,value):
        if self.onPackage :
           self.onPackage(package,value)

    def _onGetMore(self,package) :
        if self.onGetMore :
           self.onGetMore(package)

class packagesManager(Setting) :
    CONTROL = PackagesControl()
    DIALOGHEADER = _('xbian-config.packages.description')
    
    INSTALLED = _('xbian-config.packages.label.installed')
    NOTINSTALLED = _('xbian-config.packages.label.not_installed')

    def onInit(self) :
        self.control.setCallback(self.onGetMore,self.onSelect)
        self.dialog = xbmcgui.Dialog()        

    def showInfo(self,package) :
        progress = dialogWait(package,_('xbian-config.packages.loading'))
        progress.show()
        rc = xbianConfig('packages','info',package)
        progress.close()
        if rc :
            PackageInfo(package,rc[0].partition(' ')[2],rc[1].partition(' ')[2],rc[2].partition(' ')[2],rc[3].partition(' ')[2],rc[4].partition(' ')[2],rc[5].partition(' ')[2],rc[6].partition(' ')[2])

    def onSelect(self,cat,package) :        
        choice = ['Informations','Remove Package']
        select = self.dialog.select('Select',choice)
        if select == 0 :
            #display info dialog
            self.showInfo(package)
        elif select == 1 :
            #remove package
            self.APPLYTEXT = _('xbian-config.packages.remove.confirm')
            if self.askConfirmation(True) :
                self.tmppack = (cat,package)
                progressDlg = dialogWait(_('xbian-config.packages.label.remove'),_('xbian-config.common.pleasewait'))
                progressDlg.show()
                rc = xbianConfig('packages','removetest',package)
                if rc and rc[0] == '1' :
                   rc = xbianConfig('packages','remove',package)
                   if rc and rc[0] == '1' :
                       progressDlg.close()
                       dlg = dialogWaitBackground(self.DIALOGHEADER,[],self.checkInstallFinish,APTLOGFILE,skinvar=SKINVARAPTRUNNIG,onFinishedCB=self.onRemoveFinished)
                       dlg.show()
                else :
                    if rc and rc[0] == '2' :
                         #normally never pass here
                         self.ERRORTEXT = _('xbian-config.packages.not_installed')
                    elif rc and rc[0] == '3' :
                         self.ERRORTEXT = _('xbian-config.packages.essential')
                    else :
                         #normally never pass here
                         self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
                    progressDlg.close()
                    self.notifyOnError()


    def checkInstallFinish(self) :
        return xbianConfig('packages','progress')[0] != '1'

    def onInstallFinished(self) :
        time.sleep(0.5)
        self.control.addPackage(self.tmppack[0],self.tmppack[1])
        self.globalMethod['Services']['refresh']()
        self.OKTEXT = _('xbian-config.packages.install.success')
        self.notifyOnSuccess()

    def onRemoveFinished(self) :
        time.sleep(0.5)
        print self.tmppack
        self.control.removePackage(self.tmppack[0],self.tmppack[1])
        self.globalMethod['Services']['refresh']()
        self.OKTEXT = _('xbian-config.packages.remove.success')
        self.notifyOnSuccess()

    def onGetMore(self,cat) :
        progress = dialogWait(cat,_('xbian-config.packages.list.download'))
        progress.show()
        tmp = xbianConfig('packages','list',cat)
        if tmp and tmp[0] == '-3' :
            rc = xbianConfig('packages','updatedb')
            if rc[0] == '1' :
                tmp = xbianConfig('packages','list')
            else :
                tmp = []
        progress.close()
        if tmp[0]!= '-2' and tmp[0]!= '-3' :
           package = []
           for packag in tmp :
             packageTmp = packag.split(',')
             if packageTmp[1] == '0' :
                package.append(packageTmp[0])
           select =self.dialog.select(_('xbian-config.packages.name'),package)
           if select != -1 :
                choice = [_('xbian-config.packages.label.information'),_('xbian-config.packages.label.install')]
                sel = self.dialog.select('Select',choice)
                if sel == 0 :
                    #display info dialog
                    self.showInfo(package[select])
                elif sel == 1 :
                    self.APPLYTEXT = _('xbian-config.packages.install.confirm')
                    if self.askConfirmation(True) :
                        self.tmppack = (cat,package[select])
                        progressDlg = dialogWait(package[select],'xbian-config.common.pleasewait')
                        progressDlg.show()
                        rc = xbianConfig('packages','installtest',package[select])
                        if rc and rc[0] == '1' :
                             rc = xbianConfig('packages','install',package[select])
                        if rc and rc[0] == '1' :
                             progressDlg.close()
                             dlg = dialogWaitBackground(self.DIALOGHEADER,[],self.checkInstallFinish,APTLOGFILE,skinvar=SKINVARAPTRUNNIG,onFinishedCB=self.onInstallFinished)
                             dlg.show()
                        else :
                            if rc and rc[0] == '2' :
                                self.ERRORTEXT = _('xbian-config.packages.already_installed')
                            elif rc and rc[0] == '3' :
                                self.ERRORTEXT = _('xbian-config.packages.unavailable_version')
                            elif rc and rc[0] == '4' :
                                self.ERRORTEXT = _('xbian-config.packages.unavailable_version')
                            elif rc and rc[0] == '5' :
                                self.ERRORTEXT = _('xbian-config.packages.downgrade')
                            elif rc and rc[0] == '6' :
                                self.ERRORTEXT = _('xbian-config.packages.size_mismatch')
                            elif rc and rc[0] == '7' :
                                self.ERRORTEXT = _('xbian-config.packages.error')
                            else :
                                #normally never pass here
                                self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
                            progressDlg.close()
                            self.notifyOnError()


    def getXbianValue(self):
        packagesGroup = self.control.packages
        for group in packagesGroup :
            if group.hasInstalledPackage() :
                tmp = xbianConfig('packages','list',group.getName())
                if tmp[0]!= '-2' and tmp[0]!= '-3' :
                    for package in filter(lambda x : int(x[1]),map(lambda x : x.split(','),tmp)) :
                       group.addPackage(package[0])
            else :
                group.enableGetMore()

class packages(Category) :
    TITLE = _('xbian-config.packages.name')
    SETTINGS = [packagesManager]



