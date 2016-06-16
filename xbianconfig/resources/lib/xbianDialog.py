import traceback
from xbmcguie.window import DialogSkinXml
import xbmc


class XbianDialog(DialogSkinXml):

    def init(self):
        xbmc.log('XBian-config : Init XbianDialog', xbmc.LOGDEBUG)
        self.settings = []
        self.stopRequested = False
        self.title = ""
        self.queue = None

    def initialise(self, title, queue):
        self.title = title
        self.queue = queue

    def onInit(self):
        xbmc.log('XBian-config : Show(onInit) XbianDialog', xbmc.LOGDEBUG)
        for setting in self.settings:
            setting.addQueue(self.queue)
            self.addControl(setting.getControl())
        DialogSkinXml.onInit(self)
        # set title
        self.getControl(20).setLabel(self.title.title() + ' ' + _('Loading') +'...')
        for setting in self.settings:
            self._loadSettingValue(setting)
        self.getControl(20).setLabel(self.title.title())
        xbmc.log('XBian-config : End Show(onInit) XbianDialog', xbmc.LOGDEBUG)

    def _loadSettingValue(self, setting):
        try:
            setting.updateFromXbian()
        except:
            # don't enable control if error
            xbmc.log('XBian-config : Not catched exception(Get xbianValue) : %s - Settings will stay disabled' %
                     (traceback.format_exc()), xbmc.LOGERROR)
        else:
            setting.getControl().setEnabled(True)

    def addSetting(self, setting):
        self.settings.append(setting())

    def doXml(self, template):
        xbmc.log('XBian-config : Generate dialog xml from template : %s to %s' %
                 (template, self.xmlfile), xbmc.LOGDEBUG)
        xmltemplate = open(template)
        xmlout = open(self.xmlfile, 'w')
        for line in xmltemplate.readlines():
            if '<control type="xbian" value="settings"/>' in line:
                for setting in self.settings:
                    xmlout.write(setting.getControl().toXml())
            else:
                xmlout.write(line)
        xmltemplate.close()
        xmlout.close()
        xbmc.log('XBian-config : End Generate windows xml', xbmc.LOGDEBUG)
