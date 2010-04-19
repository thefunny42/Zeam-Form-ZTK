# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import ObjectDataManager, DictDataManager
from zeam.form.base.fields import Fields
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zeam.form.base.widgets import Widgets
from zeam.form.base.form import cloneFormData
from zeam.form.ztk.fields import SchemaField, registerSchemaField
from zeam.form.ztk.interfaces import IObjectSchemaField

from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.interface import Interface, implements
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


class ObjectSchemaField(SchemaField):
    """A collection field.
    """
    implements(IObjectSchemaField)
    objectFactory = None

    def __init__(self, field):
        super(ObjectSchemaField, self).__init__(field)
        self._object_fields = Fields(field.schema)

    def getObjectSchema(self):
        return self._field.schema

    def getObjectFields(self):
        return self._object_fields

    def getObjectFactory(self):
        if self.objectFactory is not None:
            return self.objectFactory
        schema = self.getObjectSchema()
        return getUtility(IFactory, name=schema.__identifier__)


registerSchemaField(ObjectSchemaField, schema_interfaces.IObject)


class ObjectFieldWidget(FieldWidget):
    grok.adapts(ObjectSchemaField, Interface, Interface)

    def prepareContentValue(self, value):
        if value is NO_VALUE:
            return {self.identifier: []}
        return {self.identifier: value}

    def update(self):
        super(ObjectFieldWidget, self).update()
        value = self.inputValue()
        fields = self.component.getObjectFields()
        form = cloneFormData(
            self.form, ObjectDataManager(value), self.identifier)
        self.fieldWidgets = Widgets(form=form, request=self.request)
        self.fieldWidgets.extend(fields)
        self.fieldWidgets.update()


class ObjectFieldExtractor(WidgetExtractor):
    grok.adapts(ObjectSchemaField, Interface, Interface)

    def extract(self):
        value = None
        form = cloneFormData(self.form, None, self.identifier)
        data, errors = form.extractData(self.component.getObjectFields())
        if not errors:
            factory = self.component.getObjectFactory()
            value = factory(**data)
        return (value, errors)



