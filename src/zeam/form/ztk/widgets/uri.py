# URI widget

from grokcore import component as grok
from zeam.form.ztk.fields import (
    SchemaField, SchemaFieldWidget, registerSchemaField)
from zope.schema import interfaces as schema_interfaces
from zope.interface import Interface


def register():
    registerSchemaField(URISchemaField, schema_interfaces.IURI)


class URISchemaField(SchemaField):
    """A text line field.
    """

class URIWidget(SchemaFieldWidget):
    grok.adapts(URISchemaField, Interface, Interface)
