# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import ObjectDataManager
from zeam.form.base.errors import Errors
from zeam.form.base.fields import Fields
from zeam.form.base.markers import NO_VALUE, Marker, DEFAULT
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.base.widgets import Widgets
from zeam.form.base.form import cloneFormData
from zeam.form.ztk.fields import (
    SchemaField, registerSchemaField, SchemaFieldWidget)
from zeam.form.ztk.interfaces import IObjectSchemaField

from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.interface import Interface, implements
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


def register():
    registerSchemaField(ObjectSchemaField, schema_interfaces.IObject)


class ObjectSchemaField(SchemaField):
    """A collection field.
    """
    implements(IObjectSchemaField)
    objectFactory = DEFAULT
    dataManager = ObjectDataManager

    def __init__(self, field):
        super(ObjectSchemaField, self).__init__(field)
        self.__object_fields = Fields(field.schema)

    @property
    def objectSchema(self):
        return self._field.schema

    @property
    def objectFields(self):
        return self.__object_fields

    def getObjectFactory(self):
        if self.objectFactory is not DEFAULT:
            return self.objectFactory
        schema = self.objectSchema
        return getUtility(IFactory, name=schema.__identifier__)


class ObjectFieldWidget(SchemaFieldWidget):
    grok.adapts(ObjectSchemaField, Interface, Interface)

    def prepareContentValue(self, value):
        if value is NO_VALUE:
            return {self.identifier: []}
        return {self.identifier: value}

    def update(self):
        super(ObjectFieldWidget, self).update()
        value = self.component.dataManager(self.inputValue())
        form = cloneFormData(self.form, value, self.identifier)
        self.objectWidgets = Widgets(form=form, request=self.request)
        self.objectWidgets.extend(self.component.objectFields)
        self.objectWidgets.update()


class ObjectFieldExtractor(WidgetExtractor):
    grok.adapts(ObjectSchemaField, Interface, Interface)

    def extract(self):
        is_present = self.request.form.get(self.identifier, NO_VALUE)
        if is_present is NO_VALUE:
            return (NO_VALUE, None)
        value = None
        form = cloneFormData(self.form, None, self.identifier)
        data, errors = form.extractData(self.component.objectFields)
        if not errors:
            factory = self.component.getObjectFactory()
            # Create an object with values
            value = factory(**dict(filter(
                        lambda (k, v): not isinstance(v, Marker),
                        data.items())))
            return (value, None)
        return (value, Errors(*errors, identifier=self.identifier))

