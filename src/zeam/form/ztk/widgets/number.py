# -*- coding: utf-8 -*-

from zeam.form.base.fields import Field
from zeam.form.base.interfaces import IFieldExtractionValueSetting
from zeam.form.base.markers import Marker, NO_VALUE
from zeam.form.base.widgets import FieldWidget, FieldWidgetExtractor
from zeam.form.ztk.fields import FieldCreatedEvent
from zeam.form.ztk.fields import registerSchemaField

from grokcore import component as grok
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class IntegerField(Field):
    """A integer field.
    """

    def __init__(self, title,
                 min=None,
                 max=None,
                 **options):
        # We pass min and max to Field to have them in htmlAttributes as well
        super(IntegerField, self).__init__(title, min=min, max=max, **options)
        self.min = min
        self.max = max

    def validate(self, value, form):
        error = super(IntegerField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            assert isinstance(value, (int, long, float))
            if self.min is not None and value < self.min:
                return _(u"This number is too small.")
            if self.max is not None and value > self.max:
                return _(u"This number is too big.")
        return None

# BBB
IntSchemaField = IntegerField


class IntegerFieldWidgetExtractor(FieldWidgetExtractor):
    grok.adapts(IntegerField, IFieldExtractionValueSetting, Interface)
    valueType = int
    failedMessage = _(u"This number is not a valid whole number.")

    def extract(self):
        value, error = super(IntegerFieldWidgetExtractor, self).extract()
        if error:
            return (value, error)
        if value is not NO_VALUE:
            try:
                value = self.valueType(value)
            except (ValueError, TypeError):
                return (NO_VALUE, self.failedMessage)
        return (value, error)


class FloatField(IntegerField):
    """A float field.
    """


# BBB
FloatSchemaField = FloatField


class FloatFieldWidgetExtractor(IntegerFieldWidgetExtractor):
    grok.adapts(FloatField, IFieldExtractionValueSetting, Interface)
    valueType = float
    failedMessage = _(u"This number is not a valid decimal number.")


class NumberWidget(FieldWidget):
    grok.adapts(IntegerField, Interface, Interface)
    defaultHTMLClass = ['field', 'field-number']


def IntegerSchemaFactory(schema):
    field = IntegerField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        min=schema.min,
        max=schema.max,
        interface=schema.interface,
        defaultValue=schema.default or NO_VALUE)
    notify(FieldCreatedEvent(field, schema.interface))
    return field


def FloatSchemaFactory(schema):
    field = FloatField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        min=schema.min,
        max=schema.max,
        interface=schema.interface,
        defaultValue=schema.default or NO_VALUE)
    notify(FieldCreatedEvent(field, schema.interface))
    return field


def register():
    registerSchemaField(FloatSchemaFactory, schema_interfaces.IFloat)
    registerSchemaField(IntegerSchemaFactory, schema_interfaces.IInt)
