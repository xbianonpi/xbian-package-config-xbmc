import base64

import xbmcgui

from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category, Setting
from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *
import resources.lib.translation

_ = resources.lib.translation.language.gettext

# FIXME: This is not a very good solution, but was the easiest way I found to
# migrate the previous translations for videoflags since they are used in more
# than one place. We should try to avoid that duplication instead.
_VIDEO_STRINGS = {
    'name': _("Video output"),
    'description': _("Change HDMI, CEC and overscan settings"),
    'label.videoflags': _("Video flags"),
    'update_success': _("Video flags successfully updated"),
    'hdmi_force_hotplug': _("Force HDMI output when no tv is identified"),
    'hdmi_ignore_hotplug': _("Ignore HDMI output even if a tv is connected"),
    'hdmi_ignore_cec_init': _(
        "Ignore CEC init, preventing wakeup of tv at reboot"),
    'hdmi_ignore_cec': _("Disable CEC"),
    'disable_overscan': _("Disable overscan"),
    'disable_splash': _("Disable the 'rainbow' screen at really start of RPI"),
}

dialog = xbmcgui.Dialog()


class NewtorkLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Network')))


class NetworkControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    DHCP = 'DHCP'
    STATIC = 'Static'
    MANUAL = 'Manual'
    DISABLE = 'Disable'

    def onInit(self):
        self.interface = SpinControlex(
            Tag('label', _('Select interface to configure')))
        self.addControl(self.interface)
        self.interfacelist = xbianConfig('network', 'list')
        self.interfaceValue = {}

        for interface in self.interfacelist:
            make_label = lambda s, spaces=0: '%s-%s' % (' ' * spaces, s)

            self.interfaceValue[interface] = {}
            self.interfaceValue[interface]['content'] = Content(
                Tag('label', interface), defaultSKin=False)
            self.interface.addContent(self.interfaceValue[interface]['content'])

            # create the interface group
            self.interfaceValue[interface]['group'] = MultiSettingControl(
                Tag('visible', 'StringCompare(Skin.String(%s),%s)' % (self.interface.getKey(), interface)))
            self.addControl(self.interfaceValue[interface]['group'])

            # add status control
            self.interfaceValue[interface]['status'] = ButtonControl(
                Tag('label', make_label(_('Status'), 1)))
            self.interfaceValue[interface]['group'].addControl(
                self.interfaceValue[interface]['status'])

            # check if Wifi
            self.interfaceValue[interface]['wifi'] = False
            if xbianConfig('network', 'type', interface)[0] == '1':
                self.interfaceValue[interface]['wifi'] = True
                self.interfaceValue[interface]['ssid'] = ButtonControl(
                    Tag('label', make_label(_('SSID'), 1)))
                self.interfaceValue[interface]['ssid'].onClick = lambda wifi: self.wifi(interface)
                self.interfaceValue[interface]['group'].addControl(
                    self.interfaceValue[interface]['ssid'])

            # add interface mode Control (dhcp/static/manual/disable)
            self.interfaceValue[interface]['mode'] = SpinControlex(
                Tag('label', make_label(_('Type'), 1)))
            dhcp = Content(Tag('label', self.DHCP), defaultSKin=False)
            static = Content(Tag('label', self.STATIC), defaultSKin=False)
            manual = Content(Tag('label', self.MANUAL), defaultSKin=False)
            disable = Content(Tag('label', self.DISABLE), defaultSKin=False)
            self.interfaceValue[interface]['mode'].addContent(dhcp)
            self.interfaceValue[interface]['mode'].addContent(static)
            self.interfaceValue[interface]['mode'].addContent(manual)
            self.interfaceValue[interface]['mode'].addContent(disable)
            self.interfaceValue[interface]['group'].addControl(
                self.interfaceValue[interface]['mode'])

            # add Static Group
            self.interfaceValue[interface]['staticgroup'] = MultiSettingControl(
                Tag('visible', 'StringCompare(Skin.String(%s),%s)' % (self.interfaceValue[interface]['mode'].getKey(), self.STATIC)))

            self.interfaceValue[interface]['ipadress'] = ButtonControl(
                Tag('label', make_label(_('IP Address'), 2)))
            self.interfaceValue[interface]['ipadress'].onClick = (
                lambda ipadress: ipadress.setValue(
                    getIp(_('IP Address'), ipadress.getValue())))

            self.interfaceValue[interface]['subnet'] = ButtonControl(
                Tag('label', make_label(_('Netmask'), 2)))
            self.interfaceValue[interface]['subnet'].onClick = (
                lambda subnet: subnet.setValue(
                    getIp(_('Netmask'), subnet.getValue())))

            self.interfaceValue[interface]['gateway'] = ButtonControl(
                Tag('label', make_label(_('Gateway'), 2)))
            self.interfaceValue[interface]['gateway'].onClick = (
                lambda gateway: gateway.setValue(
                    getIp(_('Gateway'), gateway.getValue())))

            self.interfaceValue[interface]['dns1'] = ButtonControl(
                Tag('label', make_label(_('Nameserver'), 2)))
            self.interfaceValue[interface]['dns1'].onClick = (
                lambda dns1: dns1.setValue(
                    getIp(make_label(_('Nameserver')), dns1.getValue())))

            self.interfaceValue[interface]['dns2'] = ButtonControl(
                Tag('label', make_label(_('Nameserver'), 2)))
            self.interfaceValue[interface]['dns2'].onClick = (
                lambda dns2: dns2.setValue(
                    getIp(make_label(_('Nameserver')), dns2.getValue())))

            self.interfaceValue[interface]['staticgroup'].addControl(
                self.interfaceValue[interface]['ipadress'])
            self.interfaceValue[interface]['staticgroup'].addControl(
                self.interfaceValue[interface]['subnet'])
            self.interfaceValue[interface]['staticgroup'].addControl(
                self.interfaceValue[interface]['gateway'])
            self.interfaceValue[interface]['staticgroup'].addControl(
                self.interfaceValue[interface]['dns1'])
            self.interfaceValue[interface]['staticgroup'].addControl(
                self.interfaceValue[interface]['dns2'])
            self.interfaceValue[interface]['group'].addControl(
                self.interfaceValue[interface]['staticgroup'])

    def setValue(self, values):
        default = values[0]
        self.interface.setValue(default)
        networkValue = values[1]
        for key in networkValue:
            value = networkValue[key]
            if value[0] == 'static':
                self.interfaceValue[key]['mode'].setValue(self.STATIC)
            elif value[0] == 'manual':
                self.interfaceValue[key]['mode'].setValue(self.MANUAL)
            elif value[0] == 'disable':
                self.interfaceValue[key]['mode'].setValue(self.DISABLE)
            else:
                self.interfaceValue[key]['mode'].setValue(self.DHCP)

            self.interfaceValue[key]['status'].setValue(value[1])
            self.interfaceValue[key]['ipadress'].setValue(value[2])
            self.interfaceValue[key]['subnet'].setValue(value[3])
            self.interfaceValue[key]['gateway'].setValue(value[4])
            self.interfaceValue[key]['dns1'].setValue(value[5])
            self.interfaceValue[key]['dns2'].setValue(value[6])

            if self.interfaceValue[key]['wifi']:
                self.interfaceValue[key]['ssid'].setValue('%s' % value[7])

    def wifi(self, interface):
        pass

    def getValue(self):
        default = self.interface.getValue()
        networkValue = {}
        for interface in self.interfacelist:
            networktmp = self.interfaceValue[interface]['group'].getValue()
            # sort to be compliant to xbianconfig
            networkValue[interface] = []
            if self.interfaceValue[interface]['wifi']:
                networkValue[interface].append(networktmp[2].lower())
                networkValue[interface].append(networktmp[0])
                networkValue[interface].append(networktmp[3])
                networkValue[interface].append(networktmp[4])
                networkValue[interface].append(networktmp[5])
                networkValue[interface].append(networktmp[6])
                networkValue[interface].append(networktmp[7])
                networkValue[interface].append(networktmp[1])
            else:
                networkValue[interface].append(networktmp[1].lower())
                networkValue[interface].append(networktmp[0])
                networkValue[interface].append(networktmp[2])
                networkValue[interface].append(networktmp[3])
                networkValue[interface].append(networktmp[4])
                networkValue[interface].append(networktmp[5])
                networkValue[interface].append(networktmp[6])
        return [default, networkValue]


class NetworkSetting(Setting):
    CONTROL = NetworkControl()
    DIALOGHEADER = _('Network')
    ERRORTEXT = _('Error')
    OKTEXT = _('OK')
    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self):
        self.control.wifi = self.connectWifi

    def reloadInterface(self, interface):
        interface_config = xbianConfig('network', 'status', interface)
        lanConfig = []
        values = dict(map(lambda x: x.split(' '), interface_config))
        guivalues = ['mode', 'state', 'ip', 'netmask',
                     'gateway', 'nameserver1', 'nameserver2', 'ssid']

        for val in guivalues:
            if val == 'ssid':
                value = values.get('ssid')
                if not value:
                    value = 'Not connected'
                else:
                    value = base64.b64decode(value)
            else:
                value = str(values.get(val))
            lanConfig.append(value)
        self.xbianValue[interface] = lanConfig
        self.setControlValue({interface: lanConfig})

    def connectWifi(self, interface):
        self.userValue = self.getUserValue()
        if self.isModified():
            progress = dialogWait(
                _('Please wait while updating...'),
                _('Reloading values for %s') % (interface, ))
            progress.show()
            self.setXbianValue(self.userValue)
            progress.close()

        if wifiConnect(interface):
            progress = dialogWait(
                _('Refresh'),
                _('Reloading values for %s') % (interface, ))
            progress.show()
            self.reloadInterface(interface)
            progress.close()
            self.OKTEXT = _('Successfully connected to %s') % (interface, )
            self.notifyOnSuccess()
        else:
            self.ERRORTEXT = _('Failed to connect to %s') % (interface, )
            self.notifyOnError()

    def setControlValue(self, value):
        self.control.setValue([self.default, value])

    def isModified(self):
        modif = False
        for key in self.userValue:
            if str(self.xbianValue[key][0]) != str(self.userValue[key][0]):
                modif = True
                break
            if self.userValue[key][0] != 'dhcp':
                j = (0, 2, 3, 4, 5, 6)
                for i in j:
                    if str(self.xbianValue[key][i]) != str(self.userValue[key][i]):
                        modif = True
                        break
        return modif

    def getUserValue(self):
        tmp = self.getControl().getValue()
        self.default = tmp[0]
        return tmp[1]

    def getXbianValue(self):
        self.default = False
        self.lanConfig = {}
        for interface in self.getControl().interfacelist:
            interface_config = xbianConfig('network', 'status', interface)
            if interface_config[2] == 'UP' or not self.default:
                self.default = interface
            self.lanConfig[interface] = []

            values = dict(map(lambda x: x.split(' '), interface_config))
            guivalues = ['mode', 'state', 'ip', 'netmask',
                         'gateway', 'nameserver1', 'nameserver2', 'ssid']
            for val in guivalues:
                if val == 'ssid':
                    value = values.get('ssid')
                    if not value:
                        value = 'Not connected'
                    else:
                        value = base64.b64decode(value)
                else:
                    value = str(values.get(val))
                self.lanConfig[interface].append(value)
        return self.lanConfig

    def setXbianValue(self, values):
        ok = True
        for interface in values:
            modified = False
            if str(values[interface][0]) != str(self.xbianValue[interface][0]):
                modified = True
            elif values[interface][0] != 'dhcp':
                j = (0, 2, 3, 4, 5, 6)
                for i in j:
                    if str(values[interface][i]) != str(self.xbianValue[interface][i]):
                        modified = True
                        break
            if modified:
                if values[interface][0].lower() == NetworkControl.DHCP.lower():
                    mode = 'dhcp'
                    cmd = [mode, interface]
                else:
                    mode = 'static'
                    cmd = [mode, interface, values[interface][2], values[interface][3],
                           values[interface][4], values[interface][5], values[interface][6], str(values[interface][0].lower())]
                rc = xbianConfig('network', *cmd)
                if not rc:
                    ok = False
                    self.ERRORTEXT = _('An unexpected error occurred')
                elif rc[0] == '1' and str(values[interface][0].lower()) != 'disable':
                    progress = dialogWait(
                        _('Restarting %s') % (interface, ), _('Please wait while updating'))
                    progress.show()
                    xbianConfig('network', 'restart', interface)
                    rc = '2'
                    lc = 0
                    while (rc == '2' or rc == '-12') and lc < 60:
                        tmp = xbianConfig('network', 'progress', interface)
                        if tmp:
                            rc = tmp[0]
                        time.sleep(1)
                        lc += 1
                    self.reloadInterface(interface)
                    progress.close()
                elif str(values[interface][0].lower()) != 'disable':
                    ok = False
                    try:
                        self.ERRORTEXT = rc[1]
                    except:
                        self.ERRORTEXT = _('An unexpected error occurred')
        return ok


class LicenceLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Licenses')))


class mpeg2License(Setting):
    DIALOGHEADER = _('MPG2 license')
    CONTROL = ButtonControl(Tag('label', DIALOGHEADER))
    OKTEXT = _('%s successfully updated') % (DIALOGHEADER, )
    BADUSERENTRYTEXT = _("A %s must be 9 or 10 characters long and looks "
                         "like 0x00000000. You can specify maximum 8 "
                         "licenses, separated by comma.") % (DIALOGHEADER, )

    def onInit(self):
        self.xbiankey = 'licensempg2'

    def getUserValue(self):
        return getText(self.DIALOGHEADER, self.getControlValue())

    def checkUserValue(self, value):
        for lic in str.split(value,','):
            keyok = ((len(lic) == 10) or (len(lic) == 9)) and lic[:2] == '0x'
            if keyok == False:
                break
        return keyok

    def getXbianValue(self):
        licenseValue = xbianConfig(self.xbiankey, 'select')
        if licenseValue and licenseValue[0][:2] == '0x':
            self.XbianLicenseCmd = 'update'
            return licenseValue[0]
        else:
            if len(licenseValue) == 0 or licenseValue[0] == "":
                self.XbianLicenseCmd = 'insert'
            else:
                self.XbianLicenseCmd = 'update'
            return '0x'

    def setXbianValue(self, value):
        rc = xbianConfig(self.xbiankey, self.XbianLicenseCmd, value)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            ok = False
        return ok


class vc1License(mpeg2License):
    DIALOGHEADER = _('VC1 license')
    CONTROL = ButtonControl(Tag('label', DIALOGHEADER))
    OKTEXT = _('%s successfully updated') % (DIALOGHEADER, )
    BADUSERENTRYTEXT = _("A %s must be 9 or 10 characters long and looks "
                         "like 0x00000000. You can specify maximum 8 "
                         "licenses, separated by comma.") % (DIALOGHEADER, )

    def onInit(self):
        self.xbiankey = 'licensevc1'


class connectivityLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Connectivity')), ADVANCED)


class videooutputControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.videooutputlist = xbianConfig('videoflags', 'list', cache=True)
        self.videooutputcontrol = {}
        for videooutput in self.videooutputlist:
            self.videooutputcontrol[videooutput] = RadioButtonControl(
                Tag('label', _VIDEO_STRINGS[videooutput]))
            self.videooutputcontrol[videooutput].onClick = lambda forwardclick: self.onClick(self)
            self.addControl(self.videooutputcontrol[videooutput])

    def setValue(self, values):
        for key in values:
            if values[key] == '1':
                boolvalue = True
            else:
                boolvalue = False
            self.videooutputcontrol[key].setValue(boolvalue)

    def getValue(self):
        rc = {}
        for videooutput in self.videooutputlist:
            rc[videooutput] = str(self.videooutputcontrol[videooutput].getValue())
        return rc


class videooutput(Setting):
    CONTROL = videooutputControl(ADVANCED)
    DIALOGHEADER = _('Connectivity')

    def onInit(self):
        self.listvalue = self.control.videooutputlist
        self.value = {}

    def getUserValue(self):
        return self.getControlValue()

    def getXbianValue(self):
        for value in self.listvalue:
            if value not in self.value:
                self.value[value] = xbianConfig('videoflags', 'select', value)[0]
        return self.value

    def setXbianValue(self, value):
        # set xbian config here
        for key in value:
            if value[key] != self.xbianValue[key]:
                rc = xbianConfig('videoflags', 'update', key, value[key])
                self.DIALOGHEADER = _VIDEO_STRINGS[key]
                break
        if rc and rc[0] == '1':
            return True
        else:
            return False


class SytemLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('System')), ADVANCED)


class hostname(Setting):
    CONTROL = ButtonControl(Tag('label', _('Hostname')), ADVANCED)
    DIALOGHEADER = _('Hostname')
    OKTEXT = _('Hostname successfully changed')

    def getUserValue(self):
        return getText(self.DIALOGHEADER, self.getControlValue())

    def checkUserValue(self, value):
        return value.isalnum()

    def getXbianValue(self):
        licenseValue = xbianConfig('hostname', 'select')
        if licenseValue:
            return licenseValue[0]
        else:
            return ''

    def setXbianValue(self, value):
        rc = xbianConfig('hostname', 'update', value)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            ok = False
        return ok


class kernel(Setting):
    CONTROL = SpinControlex(Tag('label', _('Kernel')), ADVANCED)
    DIALOGHEADER = '%s %s' % (_('Kernel'), _('Version'))
    OKTEXT = _('Successfully switched kernel versions')
    SAVEMODE = Setting.ONUNFOCUS

    def onInit(self):
        kernellist = xbianConfig('kernel', 'list')
        for kernel in kernellist:
            content = Content(Tag('label', kernel), defaultSKin=False)
            self.control.addContent(content)

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        kernelVersion = xbianConfig('kernel', 'select')
        if kernelVersion:
            return kernelVersion[0]
        else:
            return ''

    def setXbianValue(self, value):
        rc = xbianConfig('kernel', 'update', value)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            if rc[0] in ('-1', '-3'):
                self.ERRORTEXT = _('An unexpected error occurred')
            elif rc[0] == '-2':
                self.ERRORTEXT = _("You're already running this "
                                   "kernel version")
            ok = False
        return ok


class OverclockControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.overclockMode = SpinControlex(Tag('label', _('Overclocking')))
        self.addControl(self.overclockMode)
        self.overclockinglist = xbianConfig('overclocking', 'list')
        self.custom = False

        for mode in self.overclockinglist:
            content = Content(Tag('label', mode), defaultSKin=False)
            self.overclockMode.addContent(content)
            if mode == 'Custom':
                self.customOverclock = MultiSettingControl(
                    Tag('visible', 'StringCompare(Skin.String(%s),%s)' % (self.overclockMode.getKey(), mode)))
                self.Arm = ButtonControl(Tag('label', ' -Arm'))
                self.Core = ButtonControl(Tag('label', ' -Core'))
                self.Sdram = ButtonControl(Tag('label', ' -SDram'))
                self.Overvoltage = ButtonControl(Tag('label', ' -Overvoltage'))
                self.customOverclock.addControl(self.Arm)
                self.customOverclock.addControl(self.Core)
                self.customOverclock.addControl(self.Sdram)
                self.customOverclock.addControl(self.Overvoltage)
                self.addControl(self.customOverclock)
                self.custom = True

    def setValue(self, value):
        if value:
            # trick to get list in lower case
            for val in self.overclockinglist:
                if value[0] == val.lower():
                    break
            self.overclockMode.setValue(val)
            if self.custom:
                self.Arm.setValue(value[1])
                self.Arm.onClick = lambda arm: self.Arm.setValue(
                    getNumeric('Arm Overclocking', value[1], 400, 1200))
                self.Core.setValue(value[2])
                self.Core.onClick = lambda core: self.Core.setValue(
                    getNumeric('Arm Overclocking', value[2], 100, 600))
                self.Sdram.setValue(value[3])
                self.Sdram.onClick = lambda sdram: self.Sdram.setValue(
                    getNumeric('Arm Overclocking', value[3], 100, 600))
                self.Overvoltage.setValue(value[4])
                self.Overvoltage.onClick = lambda overvolt: self.Overvoltage.setValue(
                    getNumeric('Arm Overclocking', value[4], 0, 12))


class overclocking(Setting):
    CONTROL = OverclockControl(ADVANCED)
    DIALOGHEADER = _('Overclocking')
    OKTEXT = _('The overclock settings are successfully changed')
    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        values = self.control.getValue()
        if values:
            values[0] = values[0].lower()
        return values

    def getXbianValue(self):
        overclock = xbianConfig('overclocking', 'select')
        value = xbianConfig('overclocking', 'values')
        if overclock and value:
            overclock.extend(value[0].split(' '))
            return overclock
        else:
            return []

    def setXbianValue(self, value):
        if value[0] != 'custom':
            val = [value[0]]
        else:
            val = value

        rc = xbianConfig('overclocking', 'update', *val)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            if rc[0] == '-1':
                self.ERRORTEXT = "preset doesn't exist"
            elif rc[0] == '-2':
                self.ERRORTEXT = 'invalid number of arguments'
            elif rc[0] == '-3':
                self.ERRORTEXT = "non-numeric arguments"
            ok = False
        return ok


INITRAMFS_MODES = [ _('required'), _('always'), _('never') ]

class InitramfsControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False

    def onInit(self):
        self.initramfsMode = SpinControlex(Tag('label', _('Use of initramfs')))
        self.addControl(self.initramfsMode)
        self.initramfsmode = INITRAMFS_MODES

        for mode in self.initramfsmode:
            content = Content(Tag('label', mode), defaultSKin=False)
            self.initramfsMode.addContent(content)

    def setValue(self, value):
        if value:
            self.initramfsMode.setValue(value[0])


class initramfs(Setting):
    CONTROL = InitramfsControl(ADVANCED)
    DIALOGHEADER = _('Use of initramfs')
    SAVEMODE = Setting.ONUNFOCUS

    def getUserValue(self):
        return self.control.getValue()

    def getXbianValue(self):
        value = xbianConfig('kernel', 'initramfs')
        if value:
            if value[0] == 'disabled':
                value[0] = INITRAMFS_MODES[2]
            elif value[0] == 'yes':
                value[0] = INITRAMFS_MODES[1]
            else:
                value[0] = INITRAMFS_MODES[0]
            return value
        else:
            return INITRAMFS_MODES[0]

    def setXbianValue(self, value):
        if value[0] == INITRAMFS_MODES[2]:
            val = 'disabled'
        elif value[0] == INITRAMFS_MODES[1]:
            val = 'yes'
        else:
            val = 'no'
        rc = xbianConfig('kernel', 'initramfs', val)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            ok = False
        return ok


class timezone(Setting):
    CONTROL = ButtonControl(Tag('label', _('Timezone')), ADVANCED)
    DIALOGHEADER = _('Timezone')

    def setControlValue(self, value):
        self.control.setValue('%s / %s' % (value[0].title(), value[1].title()))

    def getUserValue(self):
        continentList = xbianConfig('timezone', 'list')
        continentgui = []
        have_to_stop = False
        while not have_to_stop:
            for continent in continentList:
                continentgui.append(continent.replace('_', ' ').title())
            rcr = dialog.select(_('Timezone'), continentgui)
            if rcr == -1:
                have_to_stop = True
            else:
                countrylist = xbianConfig('timezone', 'list', continentList[rcr])
                countrygui = []
                for country in countrylist:
                    countrygui.append(country.replace('_', ' ').title())
                rcc = dialog.select(_('Location'), countrygui)
                if rcc != -1:
                    return [continentList[rcr], countrylist[rcc]]
        return self.xbianValue

    def getXbianValue(self):
        timezone = xbianConfig('timezone', 'select')
        if timezone and timezone[0] != '-1':
            return(timezone[0].split(' '))
        else:
            return [_('Not Set'), _('Not Set')]

    def setXbianValue(self, value):
        rc = xbianConfig('timezone', 'update', *value)
        ok = True
        if not rc or not rc[0]:
            ok = False
        return ok


class AccountLabel(Setting):
    CONTROL = CategoryLabelControl(Tag('label', _('Accounts')))

    def onInit(self):
        # check if advanced mode is set
        # must check here and not in preference since value are read one by one when plugin start.
        # and this setting is read before preference - advanced mode
        key = 'advancedmode'
        rc = self.getSetting(key)
        if rc == '1':
            setvisiblecondition(key, True)
        else:
            setvisiblecondition(key, False)


class rootpwd(Setting):
    CONTROL = ButtonControl(Tag('label', _('Root password')), ADVANCED)
    DIALOGHEADER = _('Password:')
    OKTEXT = _('root password successfully changed')
    BADUSERENTRYTEXT = _("Passwords didn't match")

    def onInit(self):
        self.forceUpdate = True
        self.password = None
        self.key = 'rootpass'

    def checkUserValue(self, value):
        return self.password == self.confirmpwd

    def getUserValue(self):
        self.password = getText(self.DIALOGHEADER, hidden=True)
        self.confirmpwd = getText(self.DIALOGHEADER, hidden=True)
        return '*****'

    def getXbianValue(self):
        return '*****'

    def setXbianValue(self, value):
        rc = xbianConfig(self.key, 'update', self.password)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            ok = False
        return ok


class xbianpwd(rootpwd):
    CONTROL = ButtonControl(Tag('label', _('XBian password')))
    OKTEXT = _('xbian password successfully changed')

    def onInit(self):
        self.forceUpdate = True
        self.password = None
        self.key = 'xbianpass'


class sshroot(Setting):
    CONTROL = RadioButtonControl(Tag('label', _('SSH root login')), ADVANCED)
    DIALOGHEADER = _('SSH root login')

    def getUserValue(self):
        return str(self.getControlValue())

    def setControlValue(self, value):
        if value == '1':
            value = True
        else:
            value = False
        self.control.setValue(value)

    def getXbianValue(self):
        rc = xbianConfig('sshroot', 'status')
        return rc[0]

    def setXbianValue(self, value):
        if value == '1':
            cmd = 'enable'
        else:
            cmd = 'disable'
        rc = xbianConfig('sshroot', cmd)
        ok = True
        if not rc:
            ok = False
        elif rc[0] != '1':
            ok = False
        return ok

# CATEGORY CLASS


class system(Category):
    TITLE = _('System')
    SETTINGS = [NewtorkLabel, NetworkSetting, LicenceLabel, mpeg2License, vc1License, SytemLabel, hostname,
                timezone, kernel, overclocking, initramfs, AccountLabel, xbianpwd, rootpwd, sshroot, connectivityLabel, videooutput]
