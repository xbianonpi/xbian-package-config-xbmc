import xbmcgui
import wizard

class wizardDialog(xbmcgui.WindowXMLDialog) :
    def onInit(self) :        
        self.mainCtrl = self.getControl(50000)
        for cate in wizard.__all__ :
            setting = __import__('%s.%s'%('wizard',cate), globals(), locals(), [cate])
            data = getattr(setting,'DATA')            
            self.addWizard(data['smalltitle'],data['title'],data['description'],data['action'])
        
    def addWizard(self,smallTitle,title,description,action) :
        item = xbmcgui.ListItem()
        item.setLabel(smallTitle)
        item.setProperty('title',title)
        item.setLabel2(description)            
        path = 'None'
        if action != None :
             path = 'mode=1&title=%s&settings=%s'%(smallTitle,",".join(action))
        item.setProperty('path',path)
        self.mainCtrl.addItem(item)            
