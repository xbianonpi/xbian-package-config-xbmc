import sys
from xbmcguie.window import WindowSkinXml
import threading
import xbmc

ACTION_SELECT_ITEM = 7

selectAction = [ACTION_SELECT_ITEM]

class XbianWindow(WindowSkinXml):
    def init(self) :
        self.categories = []
        self.publicMethod = {}
        self.stopRequested = False
        self.menuhasfocus = True
        self.loadingCat = {}

    def onInit(self):
        WindowSkinXml.onInit(self)
        #first, get all public method
        for category in self.categories :
            xbmc.executebuiltin('Skin.SetString(%sloadingvalue,%s)'%(category.getTitle(),'Click to Load'))
            self.publicMethod[category.getTitle()] = {}
            for setting in category.getSettings():
                public = setting.getPublicMethod()
                for key in public :
                    self.publicMethod[category.getTitle()][key] = public[key]

    def onHeritFocus(self,controlId) :
        #handle listitem menu click for dynamic load value
        if controlId == 9000 :
            self.menuhasfocus = True
        else :
            self.menuhasfocus = False

    def onHeritAction(self,action) :
        if self.menuhasfocus and action==ACTION_SELECT_ITEM:
            selectCat =  xbmc.getInfoLabel('Container(9000).ListItem(0).Label')
            for category in self.categories :
                if category.getTitle() == selectCat :
                    if not self.loadingCat.has_key(selectCat) or not self.loadingCat[selectCat] :
                        #load/refresh category value
                        xbmc.executebuiltin('Skin.SetString(%sloadingvalue,%s)'%(category.getTitle(),'Loading...'))                        
                        self.loadingCat[selectCat] = True
                        print 'XBian : xbian-config : Loading/refresh categorie %s'%selectCat
                        initthread  = threading.Thread(None,self.onInitThread,None, (category,))
                        initthread.start()
                    break

    def onInitThread(self,category):
         for setting in category.getSettings():
             if self.stopRequested :
                 break
             try :
                 setting.updateFromXbian()
                 setting.setPublicMethod(self.publicMethod)
             except :
                 #don't enable control if error
                 print 'Exception in updateFromXbian for setting'
                 print sys.exc_info()
             else :
                 setting.getControl().setEnabled(True)
         xbmc.executebuiltin('Skin.SetString(%sloadingvalue,%s)'%(category.getTitle(),''))
         #not allow refresh now, problem with package that are add 2 times
         #self.loadingCat[category.getTitle()] = False

    def addCategory(self,category):
        self.categories.append(category)
        self.addControl(category.getCategory())


    def doXml(self,template) :
        xmltemplate = open(template)
        xmlout = open(self.xmlfile,'w')
        for line in xmltemplate.readlines() :
            if '<control type="xbian" value="Menucategories"/>' in line :
                for category in self.categories :
                    xmlout.write(category.getTitleContent().toXml())
            elif '<control type="xbian" value="categories"/>' in line :
                for category in self.categories :
                    xmlout.write(category.getCategory().toXml())
                    #xmlout.write(category.getScrollBar().toXml())
            else :
                xmlout.write(line)
        xmltemplate.close()
        xmlout.close()
