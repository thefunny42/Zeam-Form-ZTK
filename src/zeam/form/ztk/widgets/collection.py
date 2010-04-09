# -*- coding: utf-8 -*-

from zeam.form.base.interfaces import IField, IWidget, IWidgetExtractor
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import SchemaField, registerSchemaField
from zeam.form.ztk.interfaces import ICollectionSchemaField
from zeam.form.ztk.widgets.choice import ChoiceSchemaField, ChoiceFieldWidget

from zope import component
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


class CollectionSchemaField(SchemaField):
    """A collection field.
    """
    grok.implements(ICollectionSchemaField)
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


def newCollectionWidgetFactory(mode=u"", interface=IWidget):
    def collectionWidgetFactory(field, form, request):
        """A widget of a collection is a bit advanced. We have to adapt
        the sub-type of the field as well.
        """
        value_field = field.getValueField()
        return component.getMultiAdapter(
            (field, value_field, form, request), interface, name=mode)
    return collectionWidgetFactory


grok.global_adapter(
    newCollectionWidgetFactory(mode='input'),
    adapts=(ICollectionSchemaField, Interface, Interface),
    provides=IWidget,
    name='input')

grok.global_adapter(
    newCollectionWidgetFactory(mode='display'),
    adapts=(ICollectionSchemaField, Interface, Interface),
    provides=IWidget,
    name='display')

grok.global_adapter(
    newCollectionWidgetFactory(interface=IWidgetExtractor),
    adapts=(ICollectionSchemaField, Interface, Interface),
    provides=IWidgetExtractor)


class MultiChoiceFieldWidget(ChoiceFieldWidget):
    grok.adapts(ICollectionSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceFieldWidget, self).__init__(field, form, request)
        self.source = value_field

    def renderableChoice(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for choice in self.choices():
            yield {'token': choice.token,
                   'title': choice.title,
                   'checked': choice.token == current and 'checked' or None,
                   'id': base_id + '-' + choice.token.replace('.', '-')}


class MultiChoiceWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceWidgetExtractor, self).__init__(field, form, request)
        self.source = value_field

    def extract(self):
        # Not implemented yet
        return (NO_VALUE, None)
