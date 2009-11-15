# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.ztk.fields import SchemaField
from zeam.form.base.widgets import DisplayFieldWidget
from zope.schema import interfaces as schema_interfaces
from zeam.form.ztk.fields import registerSchemaField


class DatetimeField(SchemaField):
    """A datetime field.
    """


class DatetimeDisplayWidget(DisplayFieldWidget):
    grok.adapts(DatetimeField, None, None)

    def valueToUnicode(self, value):
        formatter = self.request.locale.dates.getFormatter('dateTime')
        return formatter.format(value)


registerSchemaField(DatetimeField, schema_interfaces.IDatetime)
