# -*- coding: utf-8 -*-

from zeam.form.base.widgets import FieldWidget, DisplayFieldWidget
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import Field, registerSchemaField

from grokcore import component as grok
from zope.i18nmessageid import MessageFactory
from zope.schema import interfaces as schema_interfaces


_ = MessageFactory("zeam.form.base")


class BooleanField(Field):
    """A boolean field.
    """

# BBB
BooleanSchemaField = BooleanField


class CheckBoxWidget(FieldWidget):
    grok.adapts(BooleanField, None, None)
    defaultHtmlClass = ['field', 'field-bool']
    defaultHtmlAttributes = set(['readonly', 'style', 'disabled'])
    alternateLayout = True


class CheckBoxDisplayWidget(DisplayFieldWidget):
    grok.adapts(BooleanField, None, None)

    def valueToUnicode(self, value):
        if bool(value):
            return _(u'Yes')
        return _(u'No')


class CheckBoxWidgetExtractor(WidgetExtractor):
    grok.adapts(BooleanField, None, None)

    def extract(self):
        value, error = WidgetExtractor.extract(self)
        if value == 'True':
            value = True
        else:
            value = False
        return (value, error)


def BooleanSchemaFactory(schema):
    field = BooleanField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=bool(schema.__dict__['default']))
    return field


def register():
    registerSchemaField(BooleanSchemaFactory, schema_interfaces.IBool)
