
from zeam.form.base import interfaces
from zeam.form.base.fields import Field
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import Widget, WidgetExtractor

from zeam.form.ztk.interfaces import ISchemaField

from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
from zope import schema
import zope.interface.interfaces

from grokcore import component as grok


class SchemaFieldFactory(grok.Adapter):
    grok.implements(interfaces.IFieldFactory)
    grok.context(zope.schema.interfaces.IField)

    def produce(self):
        interface = self.context.interface
        if not interface:
            raise ValueError("Field has no interface")
        yield interfaces.IField(self.context)


class InterfaceSchemaFieldFactory(grok.Adapter):
    grok.implements(interfaces.IFieldFactory)
    grok.context(zope.interface.interfaces.IInterface)

    def produce(self):
        for name, field in schema.getFieldsInOrder(self.context):
            yield interfaces.IField(field)


class SchemaField(Field, grok.Adapter):
    grok.provides(interfaces.IField)
    grok.implements(ISchemaField)
    grok.context(schema_interfaces.IField)

    def __init__(self, field):
        super(SchemaField, self).__init__(field.title, field.__name__)
        self.description = field.description
        self._field = field

    def validate(self, value):
        try:
            self._field.validate(value)
        except schema_interfaces.ValidationError, e:
            return e.doc()
        return None

    def fromUnicode(self, value):
        if schema_interfaces.IFromUnicode.providedBy(self._field):
            return self._field.fromUnicode(value)
        return value

    def getContentValue(self, setting):
        content = setting.getContent()
        return self._field.get(content, NO_VALUE)

    def getDefaultValue(self):
        return self._field.default


class SchemaWidgetExtractor(WidgetExtractor):
    grok.adapts(ISchemaField, interfaces.IFormCanvas, Interface)

    def extract(self):
        value, error = super(SchemaWidgetExtractor, self).extract()
        if error is not None:
            return value, error

        try:
            converted_value = self.component.fromUnicode(value)
        except schema_interfaces.ValidationError, e:
            return value, e.doc()

        return converted_value, None

