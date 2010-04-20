# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zope.schema import interfaces as schema_interfaces
from zeam.form.ztk.fields import registerSchemaField


class PasswordField(SchemaField):
    """A password field.
    """


class PasswordWidget(SchemaFieldWidget):
    grok.adapts(PasswordField, None, None)


registerSchemaField(PasswordField, schema_interfaces.IPassword)
