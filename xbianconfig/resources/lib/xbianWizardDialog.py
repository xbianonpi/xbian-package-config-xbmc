import sys
import xbmcgui
import wizard
if sys.version_info.major > 2:
    import urllib.request, urllib.parse, urllib.error
else:
    import urllib


class wizardDialog(xbmcgui.WindowXMLDialog):

    def onInit(self):
        self.mainCtrl = self.getControl(50000)
        for cate in wizard.__all__:
            setting = __import__('%s.%s' % ('wizard', cate), globals(), locals(), [cate])
            data = getattr(setting, 'DATA')
            self.addWizard(data['smalltitle'], data['title'], data['description'], data['action'])

    def addWizard(self, smallTitle, title, description, action):
        item = xbmcgui.ListItem()
        item.setLabel(smallTitle)
        item.setProperty('title', title)
        item.setLabel2(description)
        path = 'None'
        print(action)
        if action is not None:
            if sys.version_info.major > 2:
                path = 'mode=1&title=%s&settings=%s' % (urllib.parse.quote_plus(smallTitle), urllib.parse.quote_plus(",".join(action)))
            else:
                path = 'mode=1&title=%s&settings=%s' % (urllib.quote_plus(smallTitle), urllib.quote_plus(",".join(action)))
        item.setProperty('path', path)
        self.mainCtrl.addItem(item)
