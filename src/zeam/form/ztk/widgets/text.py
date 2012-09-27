# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base.fields import Field, NO_VALUE
from zeam.form.ztk.fields import FieldCreatedEvent
from zeam.form.ztk.fields import registerSchemaField
from zeam.form.base.widgets import FieldWidget
from zope.event import notify
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("zeam.form.base")


class TextField(Field):
    """A text field.
    """

    def __init__(self, title,
                 identifier=None,
                 description=u"",
                 defaultValue=NO_VALUE,
                 required=False,
                 readonly=False,
                 minLength = 0,
                 maxLength = None,
                 **htmlAttributes):
        super(TextField, self).__init__(title, identifier)
        self.description = description
        self.required = required
        self.readonly = readonly
        self.defaultValue = defaultValue
        self.minLength = minLength
        self.maxLength = maxLength
        self.htmlAttributes = htmlAttributes.copy()

    def validate(self, value, form):
        error = super(TextField, self).validate(value, form)
        if error is not None:
            return error
        if self.minLength and len(value) < self.minLength:
            return _(u"Not enough text was entered.")
        if self.maxLength and len(value) > self.maxLength:
            return _(u"Too much text was entered.")
        return None


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
        defaultValue=schema.default or NO_VALUE)
    notify(FieldCreatedEvent(field, schema.interface))
    return field


def register():
    registerSchemaField(TextSchemaFactory, schema_interfaces.IText)


