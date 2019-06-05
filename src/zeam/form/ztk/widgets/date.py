# -*- coding: utf-8 -*-

from zeam.form.base.markers import Marker, NO_VALUE
from zeam.form.base.widgets import FieldWidget, DisplayFieldWidget
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import Field, registerSchemaField

from grokcore import component as grok
from zope.i18n.format import DateTimeParseError
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class DateField(Field):
    """A date field.
    """
    valueLength = 'short'

    @property
    def valueType(self):        # Read-only
        return 'date'

    def __init__(self, title,
                 min=None,
                 max=None,
                 **options):
        super(DateField, self).__init__(title, **options)
        self.min = min
        self.max = max

    def getFormatter(self, form):
        return form.request.locale.dates.getFormatter(
            self.valueType, self.valueLength)

    def validate(self, value, form):
        error = super(DateField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            if self.min is not None and value < self.min:
                formatter = self.getFormatter(form)
                return _(u"This date is before the ${not_before}.",
                         dict(not_before=formatter.format(self.min)))
            if self.max is not None and value > self.max:
                formatter = self.getFormatter(form)
                return _(u"This date is after the ${not_after}.",
                         dict(not_after=formatter.format(self.max)))
        return None

# BBB
DateSchemaField = DateField

class DatetimeField(DateField):
    """A datetime field.
    """
    valueLength = 'short'

    @property
    def valueType(self):        # Read-only
        return 'dateTime'

# BBB
DatetimeSchemaField = DatetimeField


class DateFieldWidget(FieldWidget):
    grok.adapts(DateField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-date']

    def valueToUnicode(self, value):
        formatter = self.component.getFormatter(self.form)
        return formatter.format(value)


class DateWidgetExtractor(WidgetExtractor):
    grok.adapts(DateField, Interface, Interface)

    def extract(self):
        value, error = super(DateWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            if not len(value):
                return NO_VALUE, None
            formatter = self.component.getFormatter(self.form)
            try:
                value = formatter.parse(value)
            except (ValueError, DateTimeParseError) as error:
                return None, str(error)
        return value, error


class DateFieldDisplayWidget(DisplayFieldWidget):
    grok.adapts(DateField, Interface, Interface)

    def valueToUnicode(self, value):
        formatter = self.component.getFormatter(self.form)
        return formatter.format(value)


def DateSchemaFactory(schema):
    field = DateField(
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

def DatetimeSchemaFactory(schema):
    field = DatetimeField(
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
    registerSchemaField(DatetimeSchemaFactory, schema_interfaces.IDatetime)
    registerSchemaField(DateSchemaFactory, schema_interfaces.IDate)
