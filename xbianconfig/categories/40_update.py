import os
import random
import string

from xbmcaddon import Addon

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category, Setting
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
import resources.lib.translation

_ = resources.lib.translation.language.gettext

__addonID__ = "plugin.xbianconfig"
ADDON = Addon(__addonID__)
ADDON_DIR = ADDON.getAddonInfo("path")
ROOTDIR = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join(ROOTDIR, "resources")

APTLOGFILE = '/tmp/aptstatus'
# disable settings that need apt while installing/updating
SKINVARAPTRUNNIG = 'aptrunning'
KEYFORCECHECK = 'enableForce'


class updateControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        char_set = string.ascii_lowercase
        self.key = ''.join(random.sample(char_set, 6))
        self.keyupdateall = '%sall' % self.key
        self.nbUpdate = 15
        self.nbcanbeupdate = 0
        self.updates = []
        for i in range(self.nbUpdate):
            self.updates.append({})

        keynoupdate = ''
        for i, update in enumerate(self.updates):
            update['name'] = ButtonControl(Tag('visible', visiblecondition('%s%d' % (self.key, i))), Tag(
                'enable', '!%s' % visiblecondition(SKINVARAPTRUNNIG)))
            update['name'].onClick = lambda update: self.onUpdateClick(
                self.getCurrentUpdate(update))
            self.addControl(update['name'])
            keynoupdate += '!Control.IsVisible(%d) + ' % update['name'].getId()
        keynoupdate = keynoupdate[:-3]
        self.udpateAll = ButtonControl(Tag('label', 'Update all'), Tag('visible', visiblecondition(
            self.keyupdateall)), Tag('enable', '!%s' % visiblecondition(SKINVARAPTRUNNIG)))
        self.udpateAll.onClick = lambda updateall: self.onUpdateAll()
        self.addControl(self.udpateAll)

        setvisiblecondition(KEYFORCECHECK, False)
        self.forceCheck = ButtonControl(
            Tag('label', _('Check for system updates')),
            Tag('visible', visiblecondition(KEYFORCECHECK)),
            Tag('enable', '!%s' % (visiblecondition(SKINVARAPTRUNNIG), )))
        self.forceCheck.onClick = lambda forcecheck: self.onForceCheck()
        self.addControl(self.forceCheck)

        self.udpateNo = ButtonControl(Tag('label', ''), Tag('visible', '%s' % keynoupdate))
        self.addControl(self.udpateNo)

    def getCurrentUpdate(self, control):
        for i, update in enumerate(self.updates):
            if update['name'] == control:
                return i + 1

    def addUpdate(self, update):
        values = update.split(';')
        self.updates[int(values[0]) - 1]['name'].setLabel(values[1])
        self.updates[int(values[0]) - 1]['name'].setValue(values[3])
        setvisiblecondition('%s%d' % (self.key, int(values[0]) - 1), True)
        self.nbcanbeupdate += 1
        if self.nbcanbeupdate == 2:
            setvisiblecondition(self.keyupdateall, True)
        elif self.nbcanbeupdate == 1:
            setvisiblecondition(self.keyupdateall, False)

    def removeUpdate(self, update):
        values = update.split(';')
        setvisiblecondition('%s%d' % (self.key, int(values[0]) - 1), False)
        self.nbcanbeupdate -= 1
        if self.nbcanbeupdate == 1:
            setvisiblecondition(self.keyupdateall, False)

    def onUpdateClick(self, updateId):
        pass

    def onUpdateAll(self):
        pass

    def onForceCheck(self):
        pass


class upgradeXbianLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Updates')))


class packageUpdate(Setting):
    CONTROL = updateControl()
    DIALOGHEADER = _('Updates')
    ERRORTEXT = _('A serious error occured while processing these packages')
    OKTEXT = _('The packages are successfully updated')
    APPLYTEXT = _('Are you sure you want to update these packages?')

    def onInit(self):
        self.control.onUpdateClick = self.onUpdate
        self.control.onUpdateAll = self.onUpdateAll
        self.control.onForceCheck = self.onForceCheck
        self.needrefreshing = False
        self.keyword()

    def keyword(self):
        self.key = 'packages'

    def checkUpdateFinish(self):
        return xbianConfig('updates', 'progress')[0] != '1'

    def onUpdateFinished(self):
        os.remove(self.lockfile)
        # refresh gui
        # remove settings from gui
        for update in self.xbianValue:
            self.control.removeUpdate(update)
        # reload value
        self.xbianValue = self.getXbianValue()
        self.notifyOnSuccess()

    def onUpdate(self, updateId):
        self.lockfile = '/var/lock/.%s' % self.key
        open(self.lockfile, 'w').close()
        updateId = str(updateId)
        if self.askConfirmation(True):
            rc = xbianConfig('updates', 'install', self.key, updateId)
            if rc and rc[0] == '1':
                self.needrefreshing = True
                dlg = dialogWaitBackground(self.DIALOGHEADER, [
                ], self.checkUpdateFinish, APTLOGFILE, skinvar=SKINVARAPTRUNNIG, onFinishedCB=self.onUpdateFinished)
                dlg.show()
            else:
                if rc and rc[0] == '2':
                    self.ERRORTEXT = _(
                        'The latest versions of these packages are already installed')
                elif rc and rc[0] == '3':
                    self.ERRORTEXT = _('The packages you are trying to install could not be found')
                elif rc and rc[0] == '4':
                    self.ERRORTEXT = _('The packages you are trying to install could not be found')
                elif rc and rc[0] == '5':
                    self.ERRORTEXT = _('There is a size mismatch for the remote packages')
                elif rc and rc[0] == '6':
                    self.ERRORTEXT = _('A serious error occured while processing these packages')
                else:
                    self.ERRORTEXT = _('An unexpected error occurred')
                os.remove(self.lockfile)
                self.notifyOnError()

    def onForceCheck(self):
        setvisiblecondition(SKINVARAPTRUNNIG, True)
        self.lockfile = '/var/lock/.%s' % self.key
        open(self.lockfile, 'w').close()

        progress = dialogWait(
            _('Please wait...'),
            _('Retrieving list of upgradeable packages...'))
        progress.show()
        rc = xbianConfig('updates', 'updatedb')
        progress.close()
        if rc and rc[0] == '1':
            self.needrefreshing = True
            self.onUpdateFinished()
        setvisiblecondition(SKINVARAPTRUNNIG, False)

    def onUpdateAll(self):
        updates = '-'
        self.onUpdate(updates)

    def getXbianValue(self):
        rc = xbianConfig('updates', 'list', self.key, cache=False, forcerefresh=self.needrefreshing)
        if rc and not (rc[0] < '1'):
            for update in rc[:15]:
                self.control.addUpdate(update)
        else:
            self.control.udpateNo.setLabel(_('Update_to_date'))
        self.needrefreshing = False

        setvisiblecondition(KEYFORCECHECK, True)
        return rc


class updatePackageLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Updates')))


class UpdateLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Automatic updates')))


class updateAuto(Setting):
    CONTROL = RadioButtonControl(Tag('label', _('Auto install available updates')))
    DIALOGHEADER = _('Automatic updates')

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self, value):
        if value == '1':
            value = True
        else:
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc = xbianConfig('updates', 'enableauto')
        return rc[0]

    def setXbianValue(self, value):
        rc = xbianConfig('updates', 'enableauto', str(value))
        if rc and rc[0] == '1':
            return True
        else:
            return False


class snapAPT(Setting):
    CONTROL = RadioButtonControl(Tag('label', _('Do a snapshot with APT-GET transaction')))
    DIALOGHEADER = _('Update')

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self, value):
        if value == '1':
            value = True
        else:
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc = xbianConfig('updates', 'snapapt')
        return rc[0]

    def setXbianValue(self, value):
        rc = xbianConfig('updates', 'snapapt', str(value))
        if rc and rc[0] == '1':
            return True
        else:
            return False


class InventoryInt(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.AutoInventory = RadioButtonControl(
            Tag('label', _('Auto update package inventory')))
        self.addControl(self.AutoInventory)
        self.AutoInventoryProperty = MultiSettingControl(
            Tag('visible', 'SubString(Control.GetLabel(%d),*)' % self.AutoInventory.getId()))
        self.delay = ButtonControl(
            Tag('label', '        - %s' % (_('interval (days)'), )))
        self.delay.onClick = lambda delay: self.delay.setValue(
            getNumeric(_('interval (days)'), self.delay.getValue(), 1, 365))
        self.AutoInventoryProperty.addControl(self.delay)
        self.addControl(self.AutoInventoryProperty)

    def setValue(self, value):
        self.AutoInventory.setValue(value[0])
        self.delay.setValue(value[1])


class InventoryIntGui(Setting):
    CONTROL = InventoryInt()
    DIALOGHEADER = _('Auto update package inventory')
    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        values = self.control.getValue()
        return values

    def getXbianValue(self):
        rc = xbianConfig('updates', 'autoinventory')
        r = rc[0].split(' ')
        return [int(r[0]), r[1]]

    def setXbianValue(self, value):
        rc = xbianConfig('updates', 'autoinventory', str(value[0]), str(value[1]))
        if rc and rc[0] == '1':
            return True
        else:
            return False


class emptyLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', ''))


class update(Category):
    TITLE = _('Update')
    SETTINGS = [updatePackageLabel, packageUpdate,
                UpdateLabel, InventoryIntGui, updateAuto, snapAPT]
