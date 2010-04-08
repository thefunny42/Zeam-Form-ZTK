# -*- coding: utf-8 -*-

from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zeam.form.ztk.fields import SchemaField, registerSchemaField
from zeam.form.ztk.widgets.choice import ChoiceSchemaField
from zeam.form.base.interfaces import IField, IWidget

from zope import component
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


class CollectionSchemaField(SchemaField):
    """A collection field.
    """
    collectionType = list

    def getValueField(self):
        return IField(self._field.value_type)


registerSchemaField(CollectionSchemaField, schema_interfaces.ICollection)


class SetSchemaField(CollectionSchemaField):
    """A set field
    """
    collectionType = set


registerSchemaField(SetSchemaField, schema_interfaces.ISet)


class TupleSchemaField(CollectionSchemaField):
    """A tuple field.
    """
    collectionType = tuple

registerSchemaField(TupleSchemaField, schema_interfaces.ITuple)


def collectionWidgetFactory(field, form, request):
    """A widget of a collection is a bit advanced. We have to adapt
    the sub-type of the field as well.
    """
    value_field = field.getValueField()
    return getMultiAdapter(field, value_field, form, request)


grok.global_adapter(
    collectionWidgetFactory,
    adapts=(CollectionSchemaField, Interface, Interface),
    provides=IWidget,
    name='input')


class MultiChoiceFieldWidget(FieldWidget)
    grok.adapts(CollectionSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, request, form):
        super(ChoiceFieldWidget, self).__init__(field, request, form)
        self.value_field = value_field


