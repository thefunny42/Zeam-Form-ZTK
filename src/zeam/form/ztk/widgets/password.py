# -*- coding: utf-8 -*-

from zeam.form.base.fields import Field
from zeam.form.base.markers import Marker, NO_VALUE
from zeam.form.base.widgets import FieldWidget
from zeam.form.ztk.fields import registerSchemaField

from grokcore import component as grok
from zope.i18nmessageid import MessageFactory
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class PasswordField(Field):
    """A password field.
    """

    def __init__(self, title,
                 minLength=0,
                 maxLength=None,
                 **options):
        super(PasswordField, self).__init__(title, **options)
        self.minLength = minLength
        self.maxLength = maxLength

    def validate(self, value, form):
        error = super(PasswordField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            assert isinstance(value, basestring)
            if self.minLength and len(value) < self.minLength:
                return _(u"This password is too short.")
            if self.maxLength and len(value) > self.maxLength:
                return _(u"This password is too long.")
        return None


class PasswordWidget(FieldWidget):
    grok.adapts(PasswordField, None, None)
    defaultHtmlClass = ['field', 'field-password']
    defaultHtmlAttributes = ['readonly', 'required', 'autocomplete',
                             'maxlength', 'pattern', 'placeholder',
                             'size', 'style']


def PasswordSchemaFactory(schema):
    field = PasswordField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        minLength=schema.min_length,
        maxLength=schema.max_length,
        interface=schema.interface,
        defaultValue=schema.default or NO_VALUE)
    return field


def register():
    registerSchemaField(PasswordSchemaFactory, schema_interfaces.IPassword)
