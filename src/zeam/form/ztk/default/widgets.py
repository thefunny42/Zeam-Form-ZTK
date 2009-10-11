
from zeam.form.base.widgets import FieldWidget
from zeam.form.base.interfaces import IFormCanvas
from zeam.form.ztk.fields import SchemaField, registerSchemaField

from zope.schema import interfaces as schema_interfaces
from zope.interface import Interface

from grokcore import component as grok


class PasswordSchemaField(SchemaField):
    pass

registerSchemaField(PasswordSchemaField, schema_interfaces.IPassword)


class PasswordFieldWidget(FieldWidget):
    grok.adapts(PasswordSchemaField, IFormCanvas, Interface)
