# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField
from zeam.form.base.widgets import FieldWidget
from zope.schema import interfaces as schema_interfaces
from zeam.form.ztk.fields import registerSchemaField


class TextField(SchemaField):
    """A text field.
    """
    

class TextWidget(FieldWidget):
    grok.adapts(TextField, None, None)


registerSchemaField(TextField, schema_interfaces.IText)
