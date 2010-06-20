# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces


def register():
    registerSchemaField(TextSchemaField, schema_interfaces.IText)


class TextSchemaField(SchemaField):
    """A text field.
    """


class TextFieldWidget(SchemaFieldWidget):
    grok.adapts(TextSchemaField, Interface, Interface)
