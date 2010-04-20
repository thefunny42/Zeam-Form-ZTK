# Text line widget

from grokcore import component as grok
from zeam.form.ztk.fields import (
    SchemaField, SchemaFieldWidget, registerSchemaField)
from zope.schema import interfaces as schema_interfaces


class TextLineSchemaField(SchemaField):
    """A text line field.
    """

registerSchemaField(TextLineSchemaField, schema_interfaces.ITextLine)


class TextLineWidget(SchemaFieldWidget):
    grok.adapts(TextLineSchemaField, None, None)


