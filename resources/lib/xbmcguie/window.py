import os
import xbmcgui

class WindowSkinXml(xbmcgui.WindowXML):   
    def __init__(self,strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False):
        self.xmlfile = os.path.join(strFallbackPath,'resources','skins','Default','720p',strXMLname)
        self.categories = []
    
    def onInit(self):
        #set the windows instance in all xbmc control
        for category in self.categories :
            category.getCategory().setWindowInstance(self)
            #set default value to gui
            for setting in category.getSettings():
                setting.updateFromXbian()
    
    def addCategory(self,category):        
        self.categories.append(category)
     
    def doXml(self,template) :       
        xmltemplate = open(template)
        xmlout = open(self.xmlfile,'w')
        for line in xmltemplate.readlines() :
            if '<control type="xbian" value="Menucategories"/>' in line :
                for category in self.categories :
                    xmlout.write(category.getTitleContent().toXml())
            elif '<control type="xbian" value="categories"/>' in line :
                for category in self.categories :
                    print category
                    xmlout.write(category.getCategory().toXml())
            else :
                xmlout.write(line)
        xmltemplate.close()
        xmlout.close() 
        
    def onClick(self, controlID):
        for category in self.categories :
            category.onClick(controlID)
 
    def onFocus(self, controlID):
        #xbmcgui.Dialog().yesno('onFocus',str(controlID))
        pass

