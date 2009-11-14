
from zeam.form.base.widgets import FieldWidget, DisplayFieldWidget, \
    WidgetExtractor
from zeam.form.base.markers import NO_VALUE
from zeam.form.ztk.fields import SchemaField, registerSchemaField

from zope.schema import interfaces as schema_interfaces
from zope.interface import Interface

from grokcore import component as grok


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
