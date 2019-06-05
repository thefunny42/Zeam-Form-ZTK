# -*- coding: utf-8 -*-

from zeam.form.base import interfaces
from zeam.form.base.fields import Field as BaseField
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zeam.form.ztk.interfaces import ISchemaField, IFieldCreatedEvent

from grokcore import component as grok
from zope import schema, component
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Invalid, implementer
from zope.schema import interfaces as schema_interfaces
from zope.schema._bootstrapinterfaces import IContextAwareDefaultFactory
import zope.interface.interfaces

_ = MessageFactory("zeam.form.base")


@implementer(IFieldCreatedEvent)
class FieldCreatedEvent:

    def __init__(self, field, interface=None, origin=None):
        self.interface = interface
        self.field = field
        self.origin = origin


@implementer(interfaces.IFieldFactory)
class SchemaFieldFactory:
    """Create form fields from a zope.schema field (by adapting it).
    """

    def __init__(self, context):
        self.context = context

    def produce(self):
        interface = self.context.interface
        if interface is None and not getattr(self.context, '__name__', None):
            raise AssertionError("Field has no interface or __name__")
        result = interfaces.IField(self.context)
        notify(FieldCreatedEvent(result, interface, self.context))
        yield result


@implementer(interfaces.IFieldFactory)
class InterfaceSchemaFieldFactory:
    """Create a set of form fields from a zope.interface by looking
    each zope.schema fields defined on it and adapting them.
    """

    def __init__(self, context):
        self.context = context

    def produce(self):
        for name, field in schema.getFieldsInOrder(self.context):
            result =  interfaces.IField(field)
            notify(FieldCreatedEvent(result, self.context, field))
            yield result


class Field(BaseField):

    def getDefaultValue(self, form):
        if self.defaultFactory is not None:
            if IContextAwareDefaultFactory.providedBy(self.defaultFactory):
                if form is None:
                    raise TypeError('defaultFactory context required.')
                default = self.defaultFactory(form.getContent()) 
            else: 
                default = self.defaultFactory()
        else:
            default = super(Field, self).getDefaultValue(form)

        if default is NO_VALUE:
            default = self.defaultValue

        if default is None:
            return NO_VALUE

        return default


@implementer(ISchemaField)
class SchemaField(BaseField):
    """A form field using a zope.schema field as settings.
    """

    def __init__(self, field):
        super(SchemaField, self).__init__(
            field.title or None, field.__name__,
            description=field.description,
            required=field.required,
            readonly=field.readonly,
            interface=field.interface)
        self._field = field

    def get_field(self):
        return self._field

    def clone(self, new_identifier=None):
        copy = self.__class__(self._field)
        copy.__dict__.update(self.__dict__)
        if new_identifier is not None:
            copy.identifier = new_identifier
        return copy

    def validate(self, value, form):
        error = super(SchemaField, self).validate(value, form)
        if error is not None:
            return error

        if value is not NO_VALUE:
            context = None
            if form is not None:
                context = form.context
            try:
                binded_field = self._field.bind(context)
                binded_field.validate(value)
            except schema_interfaces.ValidationError as error:
                return error.doc()
            except Invalid as error:
                return error.args[0]
        return None

    def fromUnicode(self, value):
        if schema_interfaces.IFromUnicode.providedBy(self._field):
            return self._field.fromUnicode(value)
        return value

    def getDefaultValue(self, form):
        default = super(SchemaField, self).getDefaultValue(form)
        if default is not NO_VALUE:
            return default
        default = self._field.default
        if default is None:     # Zope schema use None to say no default
            return NO_VALUE
        return default


def registerSchemaField(factory, schema_field):
    # We register it by hand to have the adapter available when loading ZCML.
    component.provideAdapter(factory, (schema_field,), interfaces.IField)


class SchemaFieldWidget(FieldWidget):
    grok.adapts(ISchemaField, Interface, Interface)

    def htmlClass(self):
        css_class = ['field']
        if ISchemaField.providedBy(self.component):
            # Prevent old FieldWidget to fail if they haven't been
            # updated to the new API.
            css_class.append('field-%s' % (
                    self.component._field.__class__.__name__.lower()))
        if self.required:
            css_class.append('field-required')
        return ' '.join(css_class)


class SchemaWidgetExtractor(WidgetExtractor):
    grok.adapts(ISchemaField, Interface, Interface)

    def extract(self):
        value, error = super(SchemaWidgetExtractor, self).extract()
        if error is not None:
            return value, error

        if value is not NO_VALUE:
            try:
                value = self.component.fromUnicode(value)
            except schema_interfaces.ValidationError as e:
                return None, e.doc()
            except Invalid as e:
                return None, e.args[0]
            except ValueError as e:
                return None, _(u"Invalid value.")

        return value, None


class HiddenSchemaWidgetExtractor(SchemaWidgetExtractor):
    grok.name('hidden')


class ReadOnlySchemaWidgetExtractor(SchemaWidgetExtractor):
    grok.name('readonly')


def registerDefault():
    """Register default fields factories.
    """
    component.provideAdapter(
        SchemaFieldFactory,
        (zope.schema.interfaces.IField,))
    component.provideAdapter(
        InterfaceSchemaFieldFactory,
        (zope.interface.interfaces.IInterface,))
    registerSchemaField(SchemaField, schema_interfaces.IField)
