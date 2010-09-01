# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import DisplayFieldWidget
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField
from zope.i18n.format import DateTimeParseError
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam-form")


def register():
    registerSchemaField(TimeSchemaField, schema_interfaces.ITime)


class TimeSchemaField(SchemaField):
    """A time field.
    """


class TimeFieldWidget(SchemaFieldWidget):
    grok.adapts(TimeSchemaField, Interface, Interface)

    valueType = 'time'

    def valueToUnicode(self, value):
        locale = self.request.locale
        formatter = locale.dates.getFormatter(self.valueType, 'short')
        return formatter.format(value)


class TimeWidgetExtractor(WidgetExtractor):
    grok.adapts(TimeSchemaField, Interface, Interface)

    valueType = 'time'

    def extract(self):
        value, error = super(TimeWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            locale = self.request.locale
            formatter = locale.dates.getFormatter(self.valueType, 'short')
            try:
                value = formatter.parse(value)
            except (ValueError, DateTimeParseError), error:
                return None, str(error)
        return value, error


class TimeFieldDisplayWidget(DisplayFieldWidget):
    grok.adapts(TimeSchemaField, Interface, Interface)

    valueType = 'time'

    def valueToUnicode(self, value):
        formatter = self.request.locale.dates.getFormatter(self.valueType)
        return formatter.format(value)
