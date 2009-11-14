# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField, registerSchemaField
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zope.schema import interfaces as schema_interfaces


class BooleanField(SchemaField):
    """A boolean field.
    """


registerSchemaField(BooleanField, schema_interfaces.IBool)


class CheckBoxdWidget(FieldWidget):
    grok.adapts(BooleanField, None, None)


class CheckBoxWidgetExtractor(WidgetExtractor):
    grok.adapts(BooleanField, None, None)

    def extract(self):
        value, error = WidgetExtractor.extract(self)
        if value is NO_VALUE:
            value = False
        elif value == 'True':
            value = True
        return (value, error)
