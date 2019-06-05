# -*- coding: utf-8 -*-

import datetime

from zeam.form.base.markers import NO_VALUE, Marker
from zeam.form.base.widgets import FieldWidget, DisplayFieldWidget
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import Field, registerSchemaField

from grokcore import component as grok
from zope.i18n.format import DateTimeParseError
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class TimeField(Field):
    """A time field.
    """
    valueLength = 'short'

    def __init__(self, title,
                 min=None,
                 max=None,
                 **options):
        super(TimeField, self).__init__(title, **options)
        self.min = min
        self.max = max

    def getFormatter(self, form):
        return form.request.locale.dates.getFormatter('time', self.valueLength)

    def validate(self, value, form):
        error = super(TimeField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            assert isinstance(value, datetime.time)
            if self.min is not None and value < self.min:
                formatter = self.getFormatter(form)
                return _(u"This time is before ${not_before}.",
                         dict(not_before=formatter.format(self.min)))
            if self.max is not None and value > self.max:
                formatter = self.getFormatter(form)
                return _(u"This time is after ${not_after}.",
                         dict(not_after=formatter.format(self.max)))
        return None

# BBB
TimeSchemaField = TimeField


class TimeFieldWidget(FieldWidget):
    grok.adapts(TimeField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-time']

    def valueToUnicode(self, value):
        formatter = self.component.getFormatter(self.form)
        return formatter.format(value)


class TimeWidgetExtractor(WidgetExtractor):
    grok.adapts(TimeField, Interface, Interface)

    def extract(self):
        value, error = super(TimeWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            formatter = self.component.getFormatter(self.form)
            try:
                value = formatter.parse(value)
            except (ValueError, DateTimeParseError) as error:
                return None, str(error)
        return value, error


class TimeFieldDisplayWidget(DisplayFieldWidget):
    grok.adapts(TimeField, Interface, Interface)

    def valueToUnicode(self, value):
        formatter = self.component.getFormatter(self.form)
        return formatter.format(value)


def TimeSchemaFactory(schema):
    field = TimeField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        min=schema.min,
        max=schema.max,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.__dict__['default'] or NO_VALUE)
    return field

def register():
    registerSchemaField(TimeSchemaFactory, schema_interfaces.ITime)
