# Text line widget

import zeam.form.ztk.compat

from zeam.form.base.markers import Marker, NO_VALUE
from zeam.form.base.widgets import FieldWidget
from zeam.form.ztk.fields import Field, registerSchemaField

from grokcore import component as grok
from zope.i18nmessageid import MessageFactory
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class TextLineField(Field):
    """A text line field.
    """

    def __init__(self, title,
                 minLength=0,
                 maxLength=None,
                 **options):
        super(TextLineField, self).__init__(title, **options)
        self.minLength = minLength
        self.maxLength = maxLength

    def isEmpty(self, value):
        return value is NO_VALUE or not len(value)

    def validate(self, value, form):
        error = super(TextLineField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker) and len(value):
            assert isinstance(value, zeam.form.ztk.compat.string_types)
            if self.minLength and len(value) < self.minLength:
                return _(u"This text is too short.")
            if self.maxLength and len(value) > self.maxLength:
                return _(u"This text is too long.")
        return None


# BBB
TextLineSchemaField = TextLineField


class TextLineWidget(FieldWidget):
    grok.adapts(TextLineField, None, None)
    defaultHtmlClass = ['field', 'field-textline', 'form-control']
    defaultHtmlAttributes = set(['readonly', 'required', 'autocomplete',
                                 'maxlength', 'pattern', 'placeholder',
                                 'size', 'style', 'disabled'])


def TextLineSchemaFactory(schema):
    field = TextLineField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        minLength=schema.min_length,
        maxLength=schema.max_length,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.__dict__['default'] or NO_VALUE)
    return field


def register():
    registerSchemaField(TextLineSchemaFactory, schema_interfaces.ITextLine)
