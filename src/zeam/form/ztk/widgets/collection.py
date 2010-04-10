# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import NoneDataManager
from zeam.form.base.interfaces import IField, IWidget, IWidgetExtractor
from zeam.form.base.form import cloneSubmission
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import (
    FieldWidget, WidgetExtractor, Widgets, createWidget)
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


class MultiGenericFieldWidget(FieldWidget):
    grok.adapts(ICollectionSchemaField, Interface, Interface, Interface)

    allowAdding = True
    allowRemove = True

    def __init__(self, field, value_field, form, request):
        super(MultiGenericFieldWidget, self).__init__(field, form, request)
        self.valueCount = 0
        self.valueField = value_field
        self.valueForms = []
        self.valueWidgets = Widgets()

    def prepareValue(self, value):
        if value is NO_VALUE:
            return {self.identifier: []}
        return {self.identifier: value}

    def createValueWidgets(self):
        # We create a form submission per widget in order to have a
        # different getContent, one for each content for each widget.
        values = self.inputValue()
        if values is not NO_VALUE:
            for position, value in enumerate(values):
                field = self.valueField.copy()
                form = cloneSubmission(self.form, NoneDataManager(value))
                form.prefix = '%s.%d' % (self.identifier, position)
                widget = createWidget(field, form, self.request)
                if widget is not None:
                    self.valueForms.append(form)
                    self.valueWidgets.append(widget)
            self.valueCount = len(values)
        if not self.valueCount:
            self.allowRemove = False

    def update(self):
        super(MultiGenericFieldWidget, self).update()
        self.createValueWidgets()
        self.valueWidgets.update()


class MultiGenericWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionSchemaField, Interface, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiGenericWidgetExtractor, self).__init__(field, form, request)
        self.source = value_field

    def extract(self):
        # Not implemented yet
        return (NO_VALUE, None)


class MultiChoiceFieldWidget(ChoiceFieldWidget):
    grok.adapts(ICollectionSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceFieldWidget, self).__init__(field, form, request)
        self.source = value_field

    def prepareValue(self, value):
        if value is NO_VALUE:
            return {self.identifier: []}
        return {self.identifier: value}

    def renderableChoice(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for choice in self.choices():
            yield {'token': choice.token,
                   'title': choice.title,
                   'checked': choice.token in current and 'checked' or None,
                   'id': base_id + '-' + choice.token.replace('.', '-')}


class MultiChoiceWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceWidgetExtractor, self).__init__(field, form, request)
        self.source = value_field

    def extract(self):
        import pdb ; pdb.set_trace()
        # Not implemented yet
        return (NO_VALUE, None)
