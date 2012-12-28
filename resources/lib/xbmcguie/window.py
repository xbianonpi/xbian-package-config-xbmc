import os
import xbmcgui

class WindowSkinXml(xbmcgui.WindowXML):   
    def __init__(self,strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False):
        self.xmlfile = os.path.join(strFallbackPath,'resources','skins','Default','720p',strXMLname)
        self.categories = []
    
    def addCategory(self,category):
        categoryTmp = {}
        categoryTmp['menu'] = category.getTitleContent()
        categoryTmp['category'] = category.getCategory()
        self.categories.append(categoryTmp)
        #get xbian valu
        for control in category.getControls():
            control.getConfig()
    
    def doXml(self,template) :
        
        xmltemplate = open(template)
        xmlout = open(self.xmlfile,'w')
        for line in xmltemplate.readlines() :
            if '<control type="xbian" value="Menucategories"/>' in line :
                for category in self.categories :
                    xmlout.write(category['menu'].toXml())
            elif '<control type="xbian" value="categories"/>' in line :
                for category in self.categories :
                    print category
                    xmlout.write(category['category'].toXml())
            else :
                xmlout.write(line)
        xmltemplate.close()
        xmlout.close()
        
        
    
    def onInit(self):
        #set the windows instance in all xbmc control
        for category in self.categories :
            category['category'].setWindowInstance(self)
            #set default value to gui
            for control in category['category'].getControls():
                control.onLoad(control)
    
  
    
    
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        for category in self.categories :
            category['category'].click(controlID)
        #dialog.yesno('onclick',str(controlID))
        pass
 
    def onFocus(self, controlID):
        #xbmcgui.Dialog().yesno('onFocus',str(controlID))
        pass

