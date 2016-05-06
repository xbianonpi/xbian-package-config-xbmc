import xbmc

from virtualControl import ControlXml
from tag import Tag
from xbmcContainer import *

SKIN_DIR = xbmc.getSkinDir()

class scrollbarControl(ControlXml):
    FOCUSABLE = True
    XBMCDEFAULTCONTROL = 'scrollbar'
    additional_tag = ('texturesliderbackground', 'texturesliderbar', 'texturesliderbarfocus',
                      'textureslidernib', 'textureslidernibfocus', 'orientation', 'showonepage')


class ButtonControl(ControlXml):
    FOCUSABLE = True
    ACTION = True
    XBMCDEFAULTCONTROL = 'button'
    additional_tag = ('texturefocus', 'texturenofocus', 'label', 'label2', 'font', 'textcolor', 'focusedcolor',
                      'disabledcolor', 'shadowcolor', 'angle', 'align', 'aligny', 'textoffsetx', 'textoffsety', 'textwidth')

    def getValue(self):
        if hasattr(self, 'Controlinstance'):
            return self.Controlinstance.getLabel2()

    def setValue(self, value):
        if hasattr(self, 'Controlinstance'):
            self.Controlinstance.setLabel(label=self.Controlinstance.getLabel(), label2=str(value))

    def setLabel(self, value):
        if hasattr(self, 'Controlinstance'):
            self.Controlinstance.setLabel(label=str(value), label2=self.Controlinstance.getLabel2())

    def getLabel(self):
        if hasattr(self, 'Controlinstance'):
            return self.Controlinstance.getLabel()


class ApplyButtonControl(ControlXml):
    FOCUSABLE = True
    ACTION = True
    XBMCDEFAULTCONTROL = None
    # additional_tag = ('texturefocus','texturenofocus','label','label2','font','textcolor','focusedcolor','disabledcolor','shadowcolor','angle','align','aligny','textoffsetx','textoffsety','textwidth')
    additional_tag = ('label', 'label2')

    def onInit(self):
        self.controls = {}
        if not self.hasTag('onup'):
            # create a fake button to allow scroll up
            # print 'create onup'
            self.controls['FakebtnUp'] = ButtonControl(
                Tag('description', 'hidden button to scroll up the list'), Tag('visible', 'false'), defaultSKin=False)
            ControlXml.setTag(self, Tag('onup', self.controls['FakebtnUp'].getId()))
            # print self.tags

        if not self.hasTag('ondown'):
            # create a fake button to allow scroll down
            self.controls['FakebtnDown'] = ButtonControl(
                Tag('description', 'hidden button to scroll down the list'), Tag('visible', 'false'), defaultSKin=False)
            ControlXml.setTag(self, Tag('ondown', self.controls['FakebtnDown'].getId()))

        # print self.tags
        # create the groupControl
        self.controls['groupControl'] = GroupControl(*self.getArrayTags())
        self.controls['ApplyButtonControl'] = ButtonControl(*self.getArrayTags(), defaultSKin=False)
        self.controls['ApplyButtonControl'].setTag(Tag('align', 'center'))
        self.controls['ApplyButtonControl'].setTag(Tag('width', '150'))
        self.controls['ApplyButtonControl'].setTag(
            Tag('height', '%d' % (self.getTag('height').getValue()['value'] - 10)))
        self.controls['ApplyButtonControl'].setTag(Tag('posy', '5'))
        self.controls['ApplyButtonControl'].setTag(
            Tag('posx', '%d' % (self.getTag('width').getValue()['value'] - 160)))
        self.controls['groupControl'].addControl(self.controls['ApplyButtonControl'])
        # self.setTag(Tag('texturefocus',None))
        # self.setTag(Tag('texturenofocus',None))

    def getId(self):
        return self.controls['ApplyButtonControl'].getId()

    def setTag(self, tag, append=False):
        if tag.getKey() in self.common_tag:
            self.controls['groupControl'].setTag(tag)
        if tag.getKey() in self.focusable_tag:
            self.controls['ApplyButtonControl'].setTag(tag)

    def toXml(self):
        xml = ''
        xml += self.controls['FakebtnUp'].toXml()
        xml += self.controls['groupControl'].toXml()
        xml += self.controls['FakebtnDown'].toXml()
        return xml


class CategoryLabelControl(ControlXml):
    FOCUSABLE = False
    ACTION = False
    XBMCDEFAULTCONTROL = 'label'
    additional_tag = ('align', 'aligny', 'scroll', 'label', 'info', 'number', 'angle', 'haspath',
                      'font', 'textcolor', 'shadowcolor', 'wrapmultiline', 'scrollspeed', 'scrollsuffix')

    def onInit(self):
        self.setTag(Tag('height', '%d' % (self.getTag('height').getValue()['value'] + 5)))
        self.setTag(Tag('font', 'font13_title'))
        self.setTag(Tag('shadowcolor', 'black'))
        self.setTag(Tag('aligny', 'center'))
        global SKIN_DIR
        if SKIN_DIR == 'skin.estuary':
            self.setTag(Tag('textcolor', 'white'))
            self.setTag(Tag('align', 'center'))
        else:
            self.setTag(Tag('textcolor', 'blue'))
            self.setTag(Tag('align', 'left'))

    def setLabel(self, value):
        if hasattr(self, 'Controlinstance'):
            self.Controlinstance.setLabel(str(value))


class SpinControl(ControlXml):
    FOCUSABLE = True
    ACTION = False
    XBMCDEFAULTCONTROL = 'spincontrol'
    additional_tag = ('textureup', 'textureupfocus', 'texturedown', 'texturedownfocus', 'font', 'textcolor',
                      'disabledcolor', 'shadowcolor', 'subtype', 'align', 'aligny', 'textoffsetx', 'textoffsety')


class LabelControl(ControlXml):
    FOCUSABLE = False
    ACTION = False
    XBMCDEFAULTCONTROL = 'label'
    additional_tag = ('align', 'aligny', 'scroll', 'label', 'info', 'number', 'angle', 'haspath',
                      'font', 'textcolor', 'shadowcolor', 'wrapmultiline', 'scrollspeed', 'scrollsuffix')

    def setLabel(self, value):
        if hasattr(self, 'Controlinstance'):
            self.Controlinstance.setLabel(label=str(value), label2=self.Controlinstance.getLabel2())


class RadioButtonControl(ControlXml):
    FOCUSABLE = True
    ACTION = True
    XBMCDEFAULTCONTROL = 'radiobutton'
    additional_tag = ('texturefocus', 'texturenofocus', 'textureradioon', 'textureradiooff', 'label', 'font', 'textcolor', 'focusedcolor',
                      'disabledcolor', 'shadowcolor', 'align', 'aligny', 'textoffsetx', 'textoffsety', 'selected', 'radioposx', 'radioposy', 'radiowidth', 'radioheight')

    def getValue(self):
        if hasattr(self, 'Controlinstance'):
            return self.Controlinstance.isSelected()

    def setValue(self, value):
        if hasattr(self, 'Controlinstance'):
            self.Controlinstance.setSelected(value)


class SpinControlex(ControlXml):
    FOCUSABLE = True
    ACTION = False
    XBMCDEFAULTCONTROL = None
    additional_tag = ButtonControl.additional_tag

    def onInit(self):
        self.controls = {}
        self.values = []
        self.idx = 0
        self.value = None

        if not self.hasTag('onup'):
            # create a fake button to allow scroll up
            # print 'create onup'
            self.controls['FakebtnUp'] = ButtonControl(
                Tag('description', 'hidden button to scroll up the list'), Tag('visible', 'false'), defaultSKin=False)
            ControlXml.setTag(self, Tag('onup', self.controls['FakebtnUp'].getId()))
            # print self.tags

        if not self.hasTag('ondown'):
            # create a fake button to allow scroll down
            self.controls['FakebtnDown'] = ButtonControl(
                Tag('description', 'hidden button to scroll down the list'), Tag('visible', 'false'), defaultSKin=False)
            ControlXml.setTag(self, Tag('ondown', self.controls['FakebtnDown'].getId()))

        # print self.tags
        # create the groupControl
        self.controls['groupControl'] = GroupControl(*self.getArrayTags())
        self.controls['buttondown'] = ButtonControl()
        global SKIN_DIR
        if SKIN_DIR == 'skin.estuary':
            currentProperties = [ {'key' : 'colordiffuse', 'value' : 'button_focus'} ]
            offsetX = 42
            self.controls['buttondown'].setTag(Tag('posx', 1144))
            self.controls['buttondown'].setTag(Tag('posy', 20))
            self.controls['buttondown'].setTag(Tag('width', 33))
            self.controls['buttondown'].setTag(Tag('height', 20))
            self.controls['buttondown'].setTag(Tag('texturefocus', 'arrow-light-down1-nf.png', currentProperties))
            self.controls['buttondown'].setTag(Tag('texturenofocus', 'arrow-light-down1-nf.png'))
        else:
            currentProperties = None
            offsetX = None
            self.controls['buttondown'].setTag(Tag('posx', 680))
            self.controls['buttondown'].setTag(Tag('posy', 9))
            self.controls['buttondown'].setTag(Tag('width', 33))
            self.controls['buttondown'].setTag(Tag('height', 22))
            self.controls['buttondown'].setTag(Tag('texturefocus', 'scroll-down-focus-2.png'))
            self.controls['buttondown'].setTag(Tag('texturenofocus', 'scroll-down-2.png'))
        self.controls['buttondown'].setTag(Tag('onup', self.controls['FakebtnUp'].getId()))
        self.controls['buttondown'].setTag(Tag('ondown', self.controls['FakebtnDown'].getId()))
        if not self.hasTag('onleft'):
            # hardcode on left value - don't find how to do
            self.controls['buttondown'].setTag(Tag('onleft', 9000))

        self.controls['buttonup'] = ButtonControl()
        if SKIN_DIR == 'skin.estuary':
            self.controls['buttonup'].setTag(Tag('posx', 1177))
            self.controls['buttonup'].setTag(Tag('posy', 20))
            self.controls['buttonup'].setTag(Tag('width', 33))
            self.controls['buttonup'].setTag(Tag('height', 20))
            self.controls['buttonup'].setTag(Tag('texturefocus', 'arrow-light-up1-nf.png', currentProperties))
            self.controls['buttonup'].setTag(Tag('texturenofocus', 'arrow-light-up1-nf.png'))
        else:
            self.controls['buttonup'].setTag(Tag('posx', 713))
            self.controls['buttonup'].setTag(Tag('posy', 9))
            self.controls['buttonup'].setTag(Tag('width', 33))
            self.controls['buttonup'].setTag(Tag('height', 22))
            self.controls['buttonup'].setTag(Tag('texturefocus', 'scroll-up-focus-2.png'))
            self.controls['buttonup'].setTag(Tag('texturenofocus', 'scroll-up-2.png'))
        self.controls['buttonup'].setTag(Tag('onleft', self.controls['buttondown'].getId()))
        self.controls['buttonup'].setTag(Tag('onup', self.controls['FakebtnUp'].getId()))
        self.controls['buttonup'].setTag(Tag('ondown', self.controls['FakebtnDown'].getId()))
        self.controls['buttondown'].setTag(Tag('onright', self.controls['buttonup'].getId()))
        if not self.hasTag('onright'):
            # hardcode on left value - don't find how to do
            self.controls['buttonup'].setTag(Tag('onright', 9000))

        self.controls['FakebtnLabelFocus'] = ButtonControl(*self.getArrayTags())
        self.controls['FakebtnLabelFocus'].setTag(Tag('enable', "false"))
        self.controls['FakebtnLabelFocus'].setTag(Tag('posx', 0))
        self.controls['FakebtnLabelFocus'].setTag(Tag('posy', 0))
        self.controls['FakebtnLabelFocus'].setTag(
            Tag('disabledcolor', self.getTag('focusedcolor').getValue()['value']))
        self.controls['FakebtnLabelFocus'].setTag(Tag('visible', 'Control.HasFocus(%d) | Control.HasFocus(%d)' % (
            self.controls['buttonup'].getId(), self.controls['buttondown'].getId())))
        self.controls['FakebtnLabelFocus'].setTag(
            Tag('texturenofocus', self.controls['FakebtnLabelFocus'].getTag('texturefocus').getValue()['value'], currentProperties))
        self.controls['groupControl'].addControl(self.controls['FakebtnLabelFocus'])

        self.controls['FakebtnLabelNoFocus'] = ButtonControl(*self.getArrayTags())
        self.controls['FakebtnLabelNoFocus'].setTag(Tag('enable', "false"))
        self.controls['FakebtnLabelNoFocus'].setTag(
            Tag('disabledcolor', self.getTag('textcolor').getValue()['value']))
        self.controls['FakebtnLabelNoFocus'].setTag(Tag('posx', 0))
        self.controls['FakebtnLabelNoFocus'].setTag(Tag('posy', 0))
        self.controls['FakebtnLabelNoFocus'].setTag(Tag('visible', '![Control.HasFocus(%d) | Control.HasFocus(%d)] + Control.IsEnabled(%d)' % (
            self.controls['buttonup'].getId(), self.controls['buttondown'].getId(), self.controls['buttonup'].getId())))
        self.controls['FakebtnLabelNoFocus'].setTag(
            Tag('texturefocus', self.controls['FakebtnLabelFocus'].getTag('texturenofocus').getValue()['value']))
        self.controls['groupControl'].addControl(self.controls['FakebtnLabelNoFocus'])

        self.controls['FakebtnLabelDisabled'] = ButtonControl(*self.getArrayTags())
        self.controls['FakebtnLabelDisabled'].setTag(Tag('enable', "false"))
        self.controls['FakebtnLabelDisabled'].setTag(Tag('posx', 0))
        self.controls['FakebtnLabelDisabled'].setTag(Tag('posy', 0))
        self.controls['FakebtnLabelDisabled'].setTag(Tag('visible', '!Control.IsEnabled(%d) + control.IsVisible(%d)' % (
            self.controls['buttondown'].getId(), self.controls['buttondown'].getId())))

        if offsetX is not None:
            self.controls['FakebtnLabelFocus'].setTag(Tag('textoffsetx', offsetX))
            self.controls['FakebtnLabelNoFocus'].setTag(Tag('textoffsetx', offsetX))
            self.controls['FakebtnLabelDisabled'].setTag(Tag('textoffsetx', offsetX))

        self.controls['groupControl'].addControl(self.controls['FakebtnLabelDisabled'])

        self.controls['groupControl'].addControl(self.controls['buttondown'])

        self.controls['groupControl'].addControl(self.controls['buttonup'])

        self.key = 'spincontrol%d' % self.getId()

    def click(self, controlId):
        if controlId == self.controls['buttonup'].getId():
            self.nextvalue()
            self.onClick(self)
        elif controlId == self.controls['buttondown'].getId():
            self.previousvalue()
            self.onClick(self)

    def previousvalue(self):
        self.idx -= 1
        if self.idx < -len(self.values):
            self.idx = -1
        self.setValue(self.values[self.idx])

    def nextvalue(self):
        self.idx += 1
        if self.idx >= len(self.values):
            self.idx = 0
        self.setValue(self.values[self.idx])

    def getId(self):
        return self.controls['buttonup'].getId()

    def getIds(self):
        return (self.controls['buttonup'].getId(), self.controls['buttondown'].getId())

    def setWindowInstance(self, instance):
        self.Windowsinstance = instance
        self.controls['buttonup'].setWindowInstance(instance)
        self.controls['buttondown'].setWindowInstance(instance)
        self.controls['FakebtnLabelFocus'].setWindowInstance(instance)
        self.controls['FakebtnLabelNoFocus'].setWindowInstance(instance)
        self.controls['FakebtnLabelDisabled'].setWindowInstance(instance)
        self.Controlinstance = self.Windowsinstance.getControl(self.getId())

    def setEnabled(self, value):
        self.controls['buttonup'].setEnabled(value)
        self.controls['buttondown'].setEnabled(value)

    def setVisible(self, value):
        self.controls['buttonup'].setVisible(value)
        self.controls['buttondown'].setVisible(value)

    def setTag(self, tag, append=False):
        if tag.getKey() in self.common_tag:
            self.controls['groupControl'].setTag(tag)
        if tag.getKey() in self.focusable_tag:
            self.controls['buttonup'].setTag(tag)
            self.controls['buttondown'].setTag(tag)

    def addContent(self, content):
        val = content.getTag('label').getValue()['value']
        self.values.append(val)
        if self.value is None:
            self.value = val

    def getKey(self):
        return self.key

    def getWrapListId(self):
        return self.controls['FakebtnLabelFocus'].getId()

    def getOnUpId(self):
        return self.controls['FakebtnDown'].getId()

    def getOnDownId(self):
        return self.controls['FakebtnUp'].getId()

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value
        value = str(value) + 15 * ' '
        xbmc.executebuiltin('Skin.SetString(%s,%s)' % (self.key, self.value))
        self.controls['FakebtnLabelFocus'].setValue(value)
        self.controls['FakebtnLabelNoFocus'].setValue(value)
        self.controls['FakebtnLabelDisabled'].setValue(value)

    def toXml(self):
        xml = ''
        if 'FakebtnUp' in self.controls:
            xml += self.controls['FakebtnUp'].toXml()
        # create the group container
        xml += self.controls['groupControl'].toXml()

        if 'FakebtnDown' in self.controls:
            xml += self.controls['FakebtnDown'].toXml()
        return xml
