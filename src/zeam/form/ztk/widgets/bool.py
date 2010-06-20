# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import (
    SchemaField, SchemaFieldWidget, registerSchemaField)
from zope.schema import interfaces as schema_interfaces


class BooleanSchemaField(SchemaField):
    """A boolean field.
    """


class CheckBoxWidget(SchemaFieldWidget):
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


def register():
    """Entry point hook.
    """
    registerSchemaField(BooleanSchemaField, schema_interfaces.IBool)
