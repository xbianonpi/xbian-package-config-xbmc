from tag import Tag
from xbmcContainer import GroupListControl,Content

import xbmc

#virtual Category Class
#bass Class for all categories

class Category():
    def __init__(self,queue) :
        self.setTitle(self.TITLE)
        self.queue = queue
        self.category  = GroupListControl(Tag('onleft',9000),Tag('onright',9000),Tag('itemgap',-1),Tag('visible','Container(9000).HasFocus(%d)'%self.Menucategory.getId()),defaultSKin = False)
        self.onInit()
    
    def onInit(self):
        pass
        
    def setTitle(self,Title) :
        self.Title = Title
        self.Menucategory = Content(Tag('label',self.Title))
        
    def queueCmd(self,ctrl,cmd,cbfunc):
        self.queue.put([ctrl,cmd,cbfunc])
        
    def CmdOk(self,title,message):
        xbmc.executebuiltin("Notification(%s,%s)"%(title,message))
    
    def cmdError(self,title,message):   
        xbmc.executebuiltin("Notification(%s,%s)"%(title,message))
        
    def addControl(self,control) :
        self.category.addControl(control)
    
    def getControls(self):
        return self.category.getControls()
        
    def getTitleContent(self):
        return self.Menucategory
    
    def getCategory(self) :
        return self.category

    
