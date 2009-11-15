# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField, registerSchemaField
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zope.schema import interfaces as schema_interfaces


class BooleanSchemaField(SchemaField):
    """A boolean field.
    """


registerSchemaField(BooleanSchemaField, schema_interfaces.IBool)


class CheckBoxWidget(FieldWidget):
    grok.adapts(BooleanSchemaField, None, None)


class CheckBoxWidgetExtractor(WidgetExtractor):
    grok.adapts(BooleanSchemaField, None, None)

    def extract(self):
        value, error = WidgetExtractor.extract(self)
        if value is NO_VALUE:
            value = False
        elif value == 'True':
            value = True
        return (value, error)
