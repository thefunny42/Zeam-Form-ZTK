# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base.widgets import DisplayFieldWidget, FieldWidget
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.base.markers import NO_VALUE
from zeam.form.ztk.fields import SchemaField
from zeam.form.ztk.fields import registerSchemaField
from zope.i18n.format import DateTimeParseError
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces


class DatetimeSchemaField(SchemaField):
    """A datetime field.
    """

registerSchemaField(DatetimeSchemaField, schema_interfaces.IDatetime)


class DateSchemaField(SchemaField):
    """A date field.
    """

registerSchemaField(DateSchemaField, schema_interfaces.IDate)


class DateFieldWidget(FieldWidget):
    grok.adapts(DateSchemaField, Interface, Interface)

    valueType = 'date'

    def valueToUnicode(self, value):
        locale = self.request.locale
        formatter = locale.dates.getFormatter(self.valueType, 'short')
        return formatter.format(value)


class DateWidgetExtractor(WidgetExtractor):
    grok.adapts(DateSchemaField, Interface, Interface)

    valueType = 'date'

    def extract(self):
        value, error = super(DateWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            locale = self.request.locale
            formatter = locale.dates.getFormatter(self.valueType, 'short')
            try:
                value = formatter.parse(value)
            except DateTimeParseError:
                return (None, u'Invalid value')
        return (value, error)


class DatetimeFieldWidget(DateFieldWidget):
    grok.adapts(DatetimeSchemaField, Interface, Interface)

    valueType = 'dateTime'


class DatetimeWidgetExtractor(DateWidgetExtractor):
    grok.adapts(DatetimeSchemaField, Interface, Interface)

    valueType = 'dateTime'


class DateFieldDisplayWidget(DisplayFieldWidget):
    grok.adapts(DateSchemaField, Interface, Interface)

    valueType = 'date'

    def valueToUnicode(self, value):
        formatter = self.request.locale.dates.getFormatter(self.valueType)
        return formatter.format(value)


class DatetimeFieldDisplayWidget(DateFieldDisplayWidget):
    grok.adapts(DatetimeSchemaField, Interface, Interface)

    valueType = 'dateTime'


