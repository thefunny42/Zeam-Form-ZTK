# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor, DisplayFieldWidget
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField
from zope.i18nmessageid import MessageFactory
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class BooleanSchemaField(SchemaField):
    """A boolean field.
    """


class CheckBoxWidget(SchemaFieldWidget):
    grok.adapts(BooleanSchemaField, None, None)


class CheckBoxDisplayWidget(DisplayFieldWidget):
    grok.adapts(BooleanSchemaField, None, None)

    def valueToUnicode(self, value):
        if bool(value):
            return _(u'Yes')
        return _(u'No')


class CheckBoxWidgetExtractor(WidgetExtractor):
    grok.adapts(BooleanSchemaField, None, None)

    def extract(self):
        value, error = WidgetExtractor.extract(self)
        if value is NO_VALUE:
            value = False
        elif value == 'True':
            value = True
        return (value, error)


def register():
    """Entry point hook.
    """
    registerSchemaField(BooleanSchemaField, schema_interfaces.IBool)
