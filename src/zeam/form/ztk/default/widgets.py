
from zeam.form.base.widgets import FieldWidget, DisplayFieldWidget, \
    WidgetExtractor
from zeam.form.base.markers import NO_VALUE
from zeam.form.ztk.fields import SchemaField, registerSchemaField

from zope.schema import interfaces as schema_interfaces
from zope.interface import Interface

from grokcore import component as grok


# Password widget

class PasswordSchemaField(SchemaField):
    pass


registerSchemaField(PasswordSchemaField, schema_interfaces.IPassword)


class PasswordFieldWidget(FieldWidget):
    grok.adapts(PasswordSchemaField, Interface, Interface)


# Text widget

class TextSchemaField(SchemaField):
    pass


registerSchemaField(TextSchemaField, schema_interfaces.ISourceText)


class TextFieldWidget(FieldWidget):
    grok.adapts(TextSchemaField, Interface, Interface)


# Checkbox widget

class BooleanSchemaField(SchemaField):
    pass


registerSchemaField(BooleanSchemaField, schema_interfaces.IBool)


class CheckBoxFieldWidget(FieldWidget):
    grok.adapts(BooleanSchemaField, Interface, Interface)


class CheckBoxWidgetExtractor(WidgetExtractor):
    grok.adapts(BooleanSchemaField, Interface, Interface)

    def extract(self):
        value, error = super(CheckBoxWidgetExtractor, self).extract()
        if value is NO_VALUE:
            value = False
        elif value == 'True':
            value = True
        return (value, error)

# Datetime

class DatetimeSchemaField(SchemaField):

    def __init__(self, field):
        super(DatetimeSchemaField, self).__init__(field)


registerSchemaField(DatetimeSchemaField, schema_interfaces.IDatetime)


class DatetimeDisplayFieldWidget(DisplayFieldWidget):
    grok.adapts(DatetimeSchemaField, Interface, Interface)

    def valueToUnicode(self, value):
        formatter = self.request.locale.dates.getFormatter('dateTime')
        return formatter.format(value)

