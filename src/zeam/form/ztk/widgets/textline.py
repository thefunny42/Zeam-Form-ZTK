# Text line widget

from grokcore import component as grok
from zeam.form.base.widgets import FieldWidget
from zeam.form.ztk.fields import SchemaField, registerSchemaField
from zope.schema import interfaces as schema_interfaces


class TextLineSchemaField(SchemaField):
    """A text line field.
    """


class TextLineWidget(FieldWidget):
    grok.adapts(TextLineSchemaField, None, None)


registerSchemaField(TextLineSchemaField, schema_interfaces.ITextLine)

