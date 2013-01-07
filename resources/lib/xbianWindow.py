import os
from xbmcguie.window import WindowSkinXml
import xbmcgui

class XbianWindow(WindowSkinXml):   
    def __init__(self,strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False) :
        WindowSkinXml.__init__(self,strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False)
        self.categories = []
    
    def onInit(self):
        WindowSkinXml.onInit(self)
        #set the windows instance in all xbmc control
        for category in self.categories :
            #set default value to gui
            for setting in category.getSettings():
                setting.updateFromXbian()
                setting.getControl().setEnabled(True)
    
    def addCategory(self,category):        
        self.categories.append(category)
        WindowSkinXml.addControl(self,category.getCategory())
     
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
