# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import ObjectDataManager
from zeam.form.base.fields import Fields
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zeam.form.base.widgets import Widgets
from zeam.form.base.form import cloneSubmission
from zeam.form.ztk.fields import SchemaField, registerSchemaField

from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


class ObjectSchemaField(SchemaField):
    """A collection field.
    """

    def getObjectSchema(self):
        return self._field.schema


registerSchemaField(ObjectSchemaField, schema_interfaces.IObject)


class ObjectFieldWidget(FieldWidget):
    grok.adapts(ObjectSchemaField, Interface, Interface)

    def prepareValue(self, value):
        if value is NO_VALUE:
            return {self.identifier: []}
        return {self.identifier: value}

    def update(self):
        super(ObjectFieldWidget, self).update()
        value = self.inputValue()
        self.form = cloneSubmission(self.form, ObjectDataManager(value))
        self.fields = Fields(self.component.getObjectSchema())
        self.fieldWidgets = Widgets(form=self.form, request=self.request)
        self.fieldWidgets.extend(self.fields)
        self.fieldWidgets.update()

