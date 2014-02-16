import traceback
from xbmcguie.window import WindowSkinXml
import threading
import xbmc

import resources.lib.translation
_ = resources.lib.translation.language.ugettext


ACTION_SELECT_ITEM = 7
ACTION_MOUSE_LEFT_CLICK = 100

#Action that trigger category loading.
selectAction = [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]

class XbianWindow(WindowSkinXml):
    def init(self) :
        xbmc.log('XBian-config : Init XbianWindow',xbmc.LOGDEBUG)
        self.categories = []
        self.publicMethod = {}
        self.stopRequested = False
        self.menuhasfocus = True
        self.loadingCat = {}

    def onInit(self):
        print 'on inint, before xbmc onInit'
        xbmc.log('XBian-config : Show(onInit) XbianWindow',xbmc.LOGDEBUG)
        WindowSkinXml.onInit(self)
        print 'on inint, after xbmc onInit'
        #first, get all public method
        for category in self.categories :
            title = category.getTitle()
            xbmc.executebuiltin('Skin.SetString(%sloadingvalue,%s)'%(title,_('xbian-config.common.clicktoload')))
            self.publicMethod[title] = {}
            self.loadingCat[title] = False
            for setting in category.getSettings():
                public = setting.getPublicMethod()
                for key in public :
                    self.publicMethod[category.getTitle()][key] = public[key]
        xbmc.log('XBian-config : End Show(onInit) XbianWindow',xbmc.LOGDEBUG) 

    def onHeritFocus(self,controlId) :
        #handle listitem menu click for dynamic load value
        if controlId == 9000 :
            self.menuhasfocus = True
        else :
            self.menuhasfocus = False

    def onHeritAction(self,action) :
        if self.menuhasfocus and action in selectAction:
            selectCat =  xbmc.getInfoLabel('Container(9000).ListItem(0).Label')            
            category =  filter(lambda x : x.getTitle() == selectCat,self.categories)[0]
            if not self.loadingCat[selectCat] :            
               xbmc.log('XBian-config : Loading value for  %s'%category.getTitle(),xbmc.LOGDEBUG)
               #load category value
               xbmc.executebuiltin('Skin.SetString(%sloadingvalue,%s)'%(category.getTitle(),'Loading...'))                        
               self.loadingCat[selectCat] = True               
               initthread  = threading.Thread(None,self.onInitThread,None, (category,))
               initthread.start()               
               xbmc.log('XBian-config : Loading value thread started for  %s'%category.getTitle(),xbmc.LOGDEBUG)
               
    def onInitThread(self,category):
         xbmc.log('XBian-config : inthread : Loading value for  %s'%category.getTitle(),xbmc.LOGDEBUG)
         for setting in category.getSettings():
             if self.stopRequested :
                 xbmc.log('XBian-config : Load value Thread stop : user cancel loading',xbmc.LOGDEBUG)
                 break
             try :
                 xbmc.log('XBian-config : inthread : Start Loading setting value for  %s -> %s'%(category.getTitle(),setting.DIALOGHEADER),xbmc.LOGDEBUG)
                 setting.updateFromXbian()
                 xbmc.log('XBian-config : inthread : Stop Loading setting value for  %s -> %s'%(category.getTitle(),setting.DIALOGHEADER),xbmc.LOGDEBUG)
                 setting.setPublicMethod(self.publicMethod)
             except :
                 #don't enable control if error
                 #xbmc.log('XBian-config : Not catched exception in %s (Get xbianValue) : %s - Settings will stay disabled'%(category.getTitle(),traceback.format_exc().split('\n')[-2]),xbmc.LOGERROR)                                  
                 xbmc.log('XBian-config : Not catched exception in %s (Get xbianValue) : %s - Settings will stay disabled'%(category.getTitle(),traceback.format_exc()),xbmc.LOGERROR)                                  
             else :
                 setting.getControl().setEnabled(True)
         xbmc.executebuiltin('Skin.SetString(%sloadingvalue,%s)'%(category.getTitle(),''))
         xbmc.log('XBian-config : End inthread : Loading value for  %s'%category.getTitle(),xbmc.LOGDEBUG)
        
    def addCategory(self,category):
        self.categories.append(category)
        xbmc.log('XBian-config : Initialise category %s'%category.TITLE,xbmc.LOGDEBUG)
        self.addControl(category.getCategory())
        xbmc.log('XBian-config : End Initialise category %s'%category.TITLE,xbmc.LOGDEBUG)

    def doXml(self,template) :
        xbmc.log('XBian-config : Generate windows xml from template : %s to %s'%(template,self.xmlfile),xbmc.LOGDEBUG)
        xmltemplate = open(template)
        xmlout = open(self.xmlfile,'w')
        for line in xmltemplate.readlines() :
            if '<control type="xbian" value="Menucategories"/>' in line :
                for category in self.categories :
                    xmlout.write(category.getTitleContent().toXml().encode('utf-8'))
            elif '<control type="xbian" value="categories"/>' in line :
                for category in self.categories :
                    xmlout.write(category.getCategory().toXml().encode('utf-8'))
                    #xmlout.write(category.getScrollBar().toXml())
            else :
                xmlout.write(line)
        xmltemplate.close()
        xmlout.close()
        xbmc.log('XBian-config : End Generate windows xml',xbmc.LOGDEBUG)
