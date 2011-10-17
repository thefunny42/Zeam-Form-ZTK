# URI widget

from grokcore import component as grok
from zeam.form.ztk.fields import (
    SchemaField, SchemaFieldWidget, registerSchemaField)
from zeam.form.base.widgets import DisplayFieldWidget
from zope.schema import interfaces as schema_interfaces
from zope.interface import Interface


def register():
    registerSchemaField(URISchemaField, schema_interfaces.IURI)


class URISchemaField(SchemaField):
    """A text line field.
    """
    target = '_self'


class URIWidget(SchemaFieldWidget):
    grok.adapts(URISchemaField, Interface, Interface)


class URIDisplayWidget(DisplayFieldWidget):
    grok.adapts(URISchemaField, Interface, Interface)
    grok.name('display')

    @property
    def target(self):
        return self.component.target
