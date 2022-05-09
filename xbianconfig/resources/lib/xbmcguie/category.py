from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.xbmcContainer import GroupListControl, Content
from resources.lib.utils import *

import xbmc
import xbmcgui
from xbmcaddon import Addon

import resources.lib.translation
_ = resources.lib.translation.language.gettext

__addonID__ = "plugin.xbianconfig"


dialog = xbmcgui.Dialog()

# virtual Category Class
# bass Class for all categories


class Category():

    def __init__(self, queue, cbProgress=None):
        self.setTitle(self.TITLE)
        self.queue = queue
        self.settings = []
        for i, setting in enumerate(self.SETTINGS):
            if cbProgress:
                cbProgress(self.TITLE, setting.DIALOGHEADER, int(
                    float(100 / len(self.SETTINGS)) * i))
            self.settings.append(setting())
        # self.scrollbar = scrollbarControl(Tag('onright',9000),Tag('posx',1060),Tag('posy',60),Tag('width',25),Tag('height',530),Tag('visible','Container(9000).HasFocus(%d)'%self.Menucategory.getId()),Tag('showonepage','false'))
        self.category = GroupListControl(Tag('onleft', 9000), Tag('onright', 9000), Tag(
            'itemgap', -1), Tag('visible', 'Container(9000).HasFocus(%d)' % self.Menucategory.getId()), defaultSKin=False)
        # self.scrollbar.setTag(Tag('onleft',self.category.getId()))
        for setting in self.settings:
            setting.addQueue(self.queue)
            self.category.addControl(setting.getControl())
        self.onInit()

    def onInit(self):
        pass

    def setTitle(self, Title):
        self.Title = Title
        self.Menucategory = Content(
            Tag('label', self.Title), Tag('label2', '$INFO[Skin.String(%sloadingvalue)]' % self.Title))

    def getTitle(self):
        return self.Title

    def queueCmd(self, setting):
        self.queue.put(setting)

    def getControls(self):
        return self.category.getControls()

    def getTitleContent(self):
        return self.Menucategory

    def getSettings(self):
        return self.settings

    def getCategory(self):
        return self.category

    def getScrollBar(self):
        return self.scrollbar


class Setting():
    CONTROL = None
    DIALOGHEADER = _("XBian")
    ERRORTEXT = _('ERROR : cannot save setting')
    OKTEXT = _('Setting has been saved')
    SAVEMODE = 0
    BADUSERENTRYTEXT = _('Data you have enter is not correct')
    APPLYTEXT = _('Are you sure to apply modification?')

    # SAVE MODE
    NONE = -1
    ONCLICK = 0
    ONUNFOCUS = 1

    ADDON = Addon(__addonID__)

    def __init__(self):
        self.preInit()
        self.control = self.CONTROL
        self.control.setTag(Tag('enable', 'false'))
        self.userValue = None
        self.xbianValue = None
        # self.clickId = self.control.getClickID()
        self.queue = None
        # self.SAVE = self.onSave
        if self.SAVEMODE == self.ONCLICK:
            self.control.onClick = self.onSave
        elif self.SAVEMODE == self.ONUNFOCUS:
            self.control.onUnFocus = self.onSave
        self.forceUpdate = False
        self.canBeUpdated = True
        self.publicMethod = {}
        self.globalMethod = None
        self.updatingSetting = False
        self.onInit()

    def preInit(self):
        # Override this method if you need to do something on start of __init__
        # don't override __init__
        pass

    def onInit(self):
        # Override this method if you need to do something on end of __init__
        # don't override __init__
        pass

    def addQueue(self, queue):
        self.queue = queue

    def getPublicMethod(self):
        return self.publicMethod

    def setPublicMethod(self, methods):
        self.globalMethod = methods

    def setSetting(self, id, value):
        return setSetting(id, value)

    def getSetting(self, id):
        return getSetting(id)

    def onSave(self, ctrl):
        self.updateFromUser()

    def getControl(self):
        return self.control

    def getControlValue(self):
        return self.control.getValue()

    def setControlValue(self, value):
        self.control.setValue(value)

    def getUserValue(self):
        # this method must be overrided if user can modify value
        # must create the user interface
        return None

    def checkUserValue(self, value):
        # this method can be overrided if user can modify value
        # check validity of user Value
        # return True if data is valid
        # False either
        return True

    def isModified(self):
        return self.userValue != self.xbianValue

    def askConfirmation(self, force=False):
        if self.getSetting('confirmationonchange') != '0' or force:
            if dialog.yesno(self.DIALOGHEADER, self.APPLYTEXT):
                return True
            else:
                return False
        else:
            return True

    def updateFromUser(self):
        if self.canBeUpdated and not self.updatingSetting:
            self.userValue = self.getUserValue()
            if self.isModified() or self.forceUpdate:
                if self.userValue and self.checkUserValue(self.userValue):
                    ok = True
                    if not self.askConfirmation():
                        ok = False
                        self.updateFromXbian()
                    if ok:
                        self.updatingSetting = True
                        self.QueueSetXbianValue(self.userValue)
                        self.setControlValue(self.userValue)
                        return True
                elif self.userValue and not self.checkUserValue(self.userValue):
                    dialog.ok(self.DIALOGHEADER, 'Bad Format', self.BADUSERENTRYTEXT)
                    self.setControlValue(self.xbianValue)

    def updateFromXbian(self):
        # dialog.ok("update from xbian",ADDON.getSetting('notifyonerror'))
        self.xbianValue = self.getXbianValue()
        self.setControlValue(self.xbianValue)

    def getXbianValue(self):
        # this method must be overrided
        # get the default Xbian Value
        return None

    def QueueSetXbianValue(self, value):
        if self.queue:
            self.queue.put([self, value])

    def notifyOnError(self, force=False, time=15000):
        if self.getSetting('notifyonerror') != '0' or force:
            xbmc.executebuiltin("Notification(%s,%s,%d)" % (self.DIALOGHEADER, self.ERRORTEXT, time))

    def notifyOnSuccess(self, force=False, time=5000):
        if self.getSetting('notifyonsuccess') == '1' or force:
            xbmc.executebuiltin("Notification(%s,%s,%d)" % (self.DIALOGHEADER, self.OKTEXT, time))

    def ThreadSetXbianValue(self, value):
        rc = self.setXbianValue(value)
        if rc is False:
            self.notifyOnError()
            self.updateFromXbian()
        elif rc is True:
            self.notifyOnSuccess()
            self.xbianValue = value
        elif rc is None:
            # need a reboot
            pass

    def setXbianValue(self, value):
        # this method must be overrided
        # set the  Xbian Value
        return True
