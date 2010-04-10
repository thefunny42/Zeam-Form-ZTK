# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base.widgets import DisplayFieldWidget
from zeam.form.ztk.fields import SchemaField
from zeam.form.ztk.fields import registerSchemaField
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces


class DatetimeSchemaField(SchemaField):
    """A datetime field.
    """

registerSchemaField(DatetimeSchemaField, schema_interfaces.IDatetime)


class DatetimeFieldDisplayWidget(DisplayFieldWidget):
    grok.adapts(DatetimeSchemaField, Interface, Interface)

    def valueToUnicode(self, value):
        formatter = self.request.locale.dates.getFormatter('dateTime')
        return formatter.format(value)


