from __future__ import print_function

import os

import xbmcgui
import xbmc
from xbmcaddon import Addon

__addonID__ = "plugin.xbianconfig"
ADDON = Addon(__addonID__)
ADDON_DIR = ADDON.getAddonInfo("path")
ROOTDIR = ADDON_DIR

ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92

SKIN_DIR = xbmc.getSkinDir()
if SKIN_DIR == 'skin.estouchy' or SKIN_DIR == 'skin.estuary':
    SKIN_RES = 'xml'
else:
    SKIN_RES = '720p'

class WindowSkinXml(xbmcgui.WindowXML):

    def __init__(self, strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False):
        global SKIN_DIR
        global SKIN_RES
        try:
            with open(os.path.join(ROOTDIR, 'resources', 'skins', SKIN_DIR, SKIN_RES, 'SettingsXbianInfo.template')):
                pass
        except IOError:
            SKIN_DIR = 'Default'
        self.xmlfile = os.path.join(
            strFallbackPath, 'resources', 'skins', SKIN_DIR, SKIN_RES, strXMLname)
        self.controls = []
        self.init()

    def onInit(self):
        # set the windows instance in all xbmc control
        for control in self.controls:
            print(control)
            control.setWindowInstance(self)

    def doXml(self, template):
        # must override this function
        # must create the xml
        pass

    def addControl(self, control):
        self.controls.append(control)

    def onClick(self, controlID):
        for control in self.controls:
            control.click(controlID)

    def onFocus(self, controlID):
        for control in self.controls:
            control.focus(controlID)
        self.onHeritFocus(controlID)

    def onAction(self, Action):
        if Action in (ACTION_PREVIOUS_MENU, ACTION_BACK):
            self.close()
        self.onHeritAction(Action)

    def onHeritAction(self, Action):
        print('super onheritaction%s' % str(Action))
        # could be herit on real window
        pass

    def onHeritFocus(self, controlID):
        # could be herit on real window
        pass


class DialogSkinXml(xbmcgui.WindowXMLDialog):

    def __init__(self, strXMLname, strFallbackPath, strDefaultName=False, forceFallback=False):
        global SKIN_DIR
        global SKIN_RES
        try:
            with open(os.path.join(ROOTDIR, 'resources', 'skins', SKIN_DIR, SKIN_RES, 'SettingsXbianDialog.template')):
                pass
        except IOError:
            SKIN_DIR = 'Default'
        self.xmlfile = os.path.join(
            strFallbackPath, 'resources', 'skins', SKIN_DIR, SKIN_RES, strXMLname)
        self.controls = []
        self.init()

    def onInit(self):
        # set the windows instance in all xbmc control
        for control in self.controls:
            control.setWindowInstance(self)

    def doXml(self, template):
        # must override this function
        # must create the xml
        pass

    def addControl(self, control):
        self.controls.append(control)

    def onClick(self, controlID):
        for control in self.controls:
            control.click(controlID)

    def onFocus(self, controlID):
        for control in self.controls:
            control.focus(controlID)
