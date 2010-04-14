
from zeam.form.base import interfaces
from zeam.form.base.fields import Field
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor

from zeam.form.ztk.interfaces import ISchemaField

from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
from zope import schema, component
import zope.interface.interfaces

from grokcore import component as grok


class SchemaFieldFactory(object):
    """Create form fields from a zope.schema field (by adapting it).
    """
    grok.implements(interfaces.IFieldFactory)

    def __init__(self, context):
        self.context = context

    def produce(self):
        interface = self.context.interface
        if not interface:
            raise ValueError("Field has no interface")
        yield interfaces.IField(self.context)


# We register it by hand to have the adapter available when loading ZCML.
component.provideAdapter(
    SchemaFieldFactory,
    (zope.schema.interfaces.IField,))


class InterfaceSchemaFieldFactory(object):
    """Create a set of form fields from a zope.interface by looking
    each zope.schema fields defined on it and adapting them.
    """
    grok.implements(interfaces.IFieldFactory)

    def __init__(self, context):
        self.context = context

    def produce(self):
        for name, field in schema.getFieldsInOrder(self.context):
            yield interfaces.IField(field)


# We register it by hand to have the adapter available when loading ZCML.
component.provideAdapter(
    InterfaceSchemaFieldFactory,
    (zope.interface.interfaces.IInterface,))


class SchemaField(Field):
    """A form field using a zope.schema field as settings.
    """
    grok.implements(ISchemaField)

    def __init__(self, field):
        super(SchemaField, self).__init__(field.title, field.__name__)
        self.description = field.description
        self.required = field.required
        self._field = field

    def clone(self, new_identifier=None):
        copy = self.__class__(self._field)
        if new_identifier is not None:
            copy.identifier = new_identifier
        return copy

    def validate(self, value):
        error = super(SchemaField, self).validate(value)
        if error is not None:
            return error

        if value is not NO_VALUE:
            try:
                # It's required to call bind on the field before
                # validate because of choice fields. We put None for
                # the time being as object (don't have them, make no
                # sense)
                binded_field  = self._field.bind(None)
                binded_field.validate(value)
            except schema_interfaces.ValidationError, error:
                return error.doc()
        return None

    def fromUnicode(self, value):
        if schema_interfaces.IFromUnicode.providedBy(self._field):
            return self._field.fromUnicode(value)
        return value

    def getDefaultValue(self):
        default = self._field.default
        if default is None:     # Zope schema use None to say no default
            return NO_VALUE
        return default


def registerSchemaField(factory, schema_field):
    # We register it by hand to have the adapter available when loading ZCML.
    component.provideAdapter(factory, (schema_field,), interfaces.IField)


registerSchemaField(SchemaField, schema_interfaces.IField)


class SchemaWidgetExtractor(WidgetExtractor):
    grok.adapts(ISchemaField, interfaces.IFormCanvas, Interface)

    def extract(self):
        value, error = super(SchemaWidgetExtractor, self).extract()
        if error is not None:
            return value, error

        if value is not NO_VALUE:
            try:
                value = self.component.fromUnicode(value)
            except schema_interfaces.ValidationError, e:
                return None, e.doc()
            except ValueError, e:
                return None, u"Invalid value"

        return value, None

