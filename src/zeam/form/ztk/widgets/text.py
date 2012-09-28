# -*- coding: utf-8 -*-

from zeam.form.base.fields import Field
from zeam.form.base.markers import Marker, NO_VALUE
from zeam.form.base.widgets import FieldWidget
from zeam.form.ztk.fields import FieldCreatedEvent
from zeam.form.ztk.fields import registerSchemaField

from grokcore import component as grok
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class TextField(Field):
    """A text field.
    """

    def __init__(self, title,
                 minLength=0,
                 maxLength=None,
                 **options):
        super(TextField, self).__init__(title, **options)
        self.minLength = minLength
        self.maxLength = maxLength

    def validate(self, value, form):
        error = super(TextField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            assert isinstance(value, basestring)
            if self.minLength and len(value) < self.minLength:
                return _(u"Not enough text was entered.")
            if self.maxLength and len(value) > self.maxLength:
                return _(u"Too much text was entered.")
        return None


# BBB
TextSchemaField = TextField


class TextareaWidget(FieldWidget):
    grok.adapts(TextField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-text']


def TextSchemaFactory(schema):
    field = TextField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        minLength=schema.min_length,
        maxLength=schema.max_length,
        interface=schema.interface,
        defaultValue=schema.default or NO_VALUE)
    notify(FieldCreatedEvent(field, schema.interface))
    return field


def register():
    registerSchemaField(TextSchemaFactory, schema_interfaces.IText)


