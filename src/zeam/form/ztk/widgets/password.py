# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zope.schema import interfaces as schema_interfaces
from zeam.form.ztk.fields import registerSchemaField


def register():
    registerSchemaField(PasswordField, schema_interfaces.IPassword)


class PasswordField(SchemaField):
    """A password field.
    """


class PasswordWidget(SchemaFieldWidget):
    grok.adapts(PasswordField, None, None)
