
from zeam.form.base import interfaces
from zeam.form.base.fields import Field
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zeam.form.ztk.interfaces import ISchemaField

from grokcore import component as grok
from zope import schema, component
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
import zope.interface.interfaces

_ = MessageFactory("zeam-form")


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
        copy.__dict__.update(self.__dict__)
        if new_identifier is not None:
            copy.identifier = new_identifier
        return copy

    def validate(self, value, context=None):
        error = super(SchemaField, self).validate(value)
        if error is not None:
            return error

        if value is not NO_VALUE:
            try:
                binded_field  = self._field.bind(context)
                binded_field.validate(value)
            except schema_interfaces.ValidationError, error:
                return error.doc()
        return None

    def fromUnicode(self, value):
        if schema_interfaces.IFromUnicode.providedBy(self._field):
            return self._field.fromUnicode(value)
        return value

    def getDefaultValue(self):
        default = super(SchemaField, self).getDefaultValue()
        if default is not NO_VALUE:
            return default
        default = self._field.default
        if default is None:     # Zope schema use None to say no default
            return NO_VALUE
        return default


def registerSchemaField(factory, schema_field):
    # We register it by hand to have the adapter available when loading ZCML.
    component.provideAdapter(factory, (schema_field,), interfaces.IField)


registerSchemaField(SchemaField, schema_interfaces.IField)


class SchemaFieldWidget(FieldWidget):
    grok.adapts(ISchemaField, Interface, Interface)

    def htmlClass(self):
        return 'field-%s' % self.component._field.__class__.__name__.lower()


class SchemaWidgetExtractor(WidgetExtractor):
    grok.adapts(ISchemaField, Interface, Interface)

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
                return None, _(u"Invalid value")

        return value, None

