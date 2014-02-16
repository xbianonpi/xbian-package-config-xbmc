from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import resources.lib.translation
_ = resources.lib.translation.language.ugettext

import xbmc,xbmcgui

import uuid

MAXGUISERVICE = 50

dialog = xbmcgui.Dialog()

#Helper Class
class Service :
    def __init__(self,onServiceCB) :
        self.onServiceCB = onServiceCB
        self.visiblekey = uuid.uuid4()
        self.label = ''
        self.control = ButtonControl(Tag('label',self.label),Tag('visible',visiblecondition(self.visiblekey)))
        self.control.onClick = self._onClick

    def getName(self) :
        return self.label

    def disable(self) :
        xbmc.log('XBian-config : Disable service %s'%self.label,xbmc.LOGDEBUG)
        setvisiblecondition(self.visiblekey,False)
        self.control.setLabel('')

    def enable(self,service,status) :
        xbmc.log('XBian-config : Enable service %s to %s'%(service,status),xbmc.LOGDEBUG)
        self.label = service        
        self.control.setLabel(self.label)
        self.control.setValue(status)
        self.control.setEnabled(True)
        setvisiblecondition(self.visiblekey,True)

    def getControl(self) :
        return self.control

    def clean(self) :
        setvisiblecondition(self.visiblekey,False)

    def _onClick(self,ctrl) :
        xbmc.log('XBian-config : on Service %s click '%self.label,xbmc.LOGDEBUG)
        self.onServiceCB(self.label)


class ServicesControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
   
    def onInit(self) :
        self.services = []
        self.initialiseIndex = 0
        self.flagRemove = False
        self.onService = None
        self.onCustom = None
        for i in xrange(MAXGUISERVICE) :
            self.services.append(Service(self._onService))
            self.addControl(self.services[-1].getControl())
        self.addControl(CategoryLabelControl(Tag('label',_('xbian-config.services.label.edit')),ADVANCED))
        self.addCustomBtn = ButtonControl(Tag('label',_('xbian-config.services.label.add_custom')),ADVANCED)
        self.addCustomBtn.onClick = self._onCustom
        self.addControl(self.addCustomBtn)
        
    def setCallback(self,onService=None,onCustom=None) :
        self.onService = onService
        self.onCustom = onCustom
          
    def addService(self,service,status,refresh=False) :
        xbmc.log('XBian-config : Add Service %s'%(service),xbmc.LOGDEBUG)
        if status : status = _('xbian-config.services.label.running')
        else : status = _('xbian-config.services.label.stopped')
            
        idx = self.initialiseIndex
        find = False
        if self.flagRemove or refresh:
            for i,serv in enumerate(self.services) :
               if serv.getName() == service :
                   find = True
                   break
            if find :
                idx = i

        if not find : self.initialiseIndex += 1
        self.services[idx].enable(service,status)
        
    def removeService(self,service) :
        xbmc.log('XBian-config : Remove service %s'%service,xbmc.LOGDEBUG)
        filter(lambda x : x.getName() == service,self.services[:self.initialiseIndex])[0].disable()       
        self.flagRemove = True        
    
    def _onService(self,service) :
        if self.onService : self.onService(service)
    
    def _onCustom(self,ctrl) :
        if self.onCustom : self.onCustom()
        
class serviceLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label',_('xbian-config.services.label.service')))


class servicesManager(Setting) :
    CONTROL = ServicesControl()
    DIALOGHEADER = _('xbian-config.services.description')
    
    def onInit(self) :        
        self.publicMethod['refresh'] = self.refresh
        self.services = {}
        self.control.setCallback(self.onService,self.onCustom)
        self.guiloaded = False
        
    def refresh(self) :
        if self.guiloaded :
            xbmc.log('XBian-config : Refresh services status',xbmc.LOGDEBUG)
            tmp = self.control.flagRemove
            self.control.flagRemove = True
            self.getXbianValue()
            self.control.flagRemove = tmp
                                    
    def onService(self,service):
        action = []
        choice = []                
        if self.services[service][0] :
            choice.append(_('xbian-config.services.label.stop'))
            action.append(('services','stop',service))
            choice.append(_('xbian-config.services.label.restart'))
            action.append(('services','restart',service))
        else :
            choice.append(_('xbian-config.services.label.start'))
            action.append(('services','start',service))
        if self.services[service][1] :
            choice.append(_('xbian-config.services.label.noautostart'))          
            action.append(('services','autostart',service,'disable'))
        else :
            choice.append(_('xbian-config.services.label.autostart'))
            action.append(('services','autostart',service,'enable'))
        choice.append(_('xbian-config.services.label.delete')) 
        action.append(('services','delete',service))
        choice.append(_('xbian-config.services.refresh_gui'))
        
        select = dialog.select(service,choice)
        if select == -1 : return
        
        self.APPLYTEXT = '%s %s?'%(_('xbian-config.common.doyouwanto')%choice[select],service)
        if self.askConfirmation() :
            #TODO
            #not clean to use translation in test
            #have to be rewrited
            if choice[select] == _('xbian-config.services.refresh_gui') :
                self.refresh()
                rc = ['1']
            else :
                print action,select
                rc = xbianConfig(*action[select])
            if not rc or rc[0] == '0' :
                self.ERRORTEXT = 'Cant %s %s'%(choice[select],service)
                self.notifyOnError()
            elif rc[0] == '1' :
                self.OKTEXT = '%s %s successfully'%(choice[select],service)
                self.notifyOnSuccess()
                if choice[select] == 'Remove from gui' :
                    self.control.removeService(service)
                    
                #refresh internal value
                #TODO
                #not clean to use translation in test
                #have to be rewrited
                if choice[select] == _('xbian-config.services.label.start') :
                    self.control.addService(service,True,True)
                    self.services[service][0] = True
                elif choice[select] == _('xbian-config.services.label.stop') :
                    self.control.addService(service,False,True)
                    self.services[service][0] = False
                elif choice[select] == _('xbian-config.services.label.noautostart') :                    
                    self.services[service][1] = False
                elif choice[select] == _('xbian-config.services.label.autostart') :                    
                    self.services[service][1] = True
            elif rc[0] == '-3' :
                self.ERRORTEXT = 'Service %s already running'%service
                self.notifyOnError()
            elif rc[0] == '-4' :
                self.ERRORTEXT = 'Service %s already stopped'%service
                self.notifyOnError()
            elif rc[0] == '-5' :
                self.ERRORTEXT = 'Autostart already enabled for %s'%service
                self.notifyOnError()
            elif rc[0] == '-6' :
                self.ERRORTEXT = 'Autostart already disabled for %s'%service
                self.notifyOnError()
            else :
                self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
                self.notifyOnError()
                    
    def onCustom(self):
        name = getText(_('xbian-config.services.label.name'))
        if not name :
            return
        self.APPLYTEXT = _('xbian-config.services.label.confirminsert')%name
        if self.askConfirmation() :
           progress = dialogWait(_('xbian-config.services.label.edit'),_('xbian-config.common.pleasewait'))
           progress.show() 
           rc = xbianConfig('services','insert',name)                                            
           if rc and rc[0] == '1' :
               #check service status
               rcs = xbianConfig('services','status',name)
               if rcs :
                   self.services[name] = self._parseStatus(int(rcs[0].split(' ')[1]))                                  
                   self.control.addService(name,self.services[name][0])
                   self.OKTEXT = _('xbian-config.services.inserted')
                   self.notifyOnSuccess()
               else :
                   self.ERRORTEXT = _('xbian-config.services.refresh')
                   self.notifyOnError()  
           elif rc and rc[0] == '-2':           
               self.ERRORTEXT = _('xbian-config.services.not_exists')
               self.notifyOnError()
           else :
               self.ERRORTEXT = _('xbian-config.dialog.unexpected_error')
               self.notifyOnError()                            
           progress.close()         
                         
    def _parseStatus(self,status) :
        if status == 5 :
            return [True,True]
        elif status == 2 :
            return [False,False]
        elif status == 4 :
            return [True,False]
        elif status == 3 :
            return [False,True]
        
    def getXbianValue(self):
        self.guiloaded = True #allow refresh.
        serviceList = xbianConfig('services','status')                
        for service in serviceList :
            tmp = service.split(' ')
            self.services[tmp[0]] = self._parseStatus(int(tmp[1]))
            self.control.addService(tmp[0],self.services[tmp[0]][0])                    
            
class services(Category) :
    TITLE = _('xbian-config.services.name')
    SETTINGS = [serviceLabel,servicesManager]    


