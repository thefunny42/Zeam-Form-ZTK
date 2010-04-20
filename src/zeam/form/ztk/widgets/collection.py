# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import NoneDataManager
from zeam.form.base.interfaces import IField, IWidget, IWidgetExtractor
from zeam.form.base.form import cloneFormData
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.fields import Fields
from zeam.form.base.widgets import WidgetExtractor, Widgets, createWidget
from zeam.form.ztk.fields import (
    SchemaField, registerSchemaField, SchemaFieldWidget)
from zeam.form.ztk.interfaces import ICollectionSchemaField
from zeam.form.ztk.widgets.choice import ChoiceSchemaField, ChoiceFieldWidget
from zeam.form.ztk.widgets.object import ObjectSchemaField

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


class MultiGenericFieldWidget(SchemaFieldWidget):
    grok.adapts(ICollectionSchemaField, Interface, Interface, Interface)

    allowAdding = True
    allowRemove = True

    def __init__(self, field, value_field, form, request):
        super(MultiGenericFieldWidget, self).__init__(field, form, request)
        self.valueField = value_field
        self.valueWidgets = Widgets()

    def newValueWidget(self, new_identifier, value):
        field = self.valueField.clone(new_identifier=str(new_identifier))
        form = cloneFormData(self.form, prefix=self.identifier)
        if value is not None:
            form.ignoreContent = False
            form.setContentData(NoneDataManager(value))
        else:
            form.ignoreRequest = False
            form.ignoreContent = True
        widget = createWidget(field, form, self.request)
        if widget is not None:
            self.valueWidgets.append(widget)

    def prepareContentValue(self, values):
        if values is NO_VALUE:
            return {self.identifier: '0'}
        for position, value in enumerate(values):
            # Create new widgets for each value
            self.newValueWidget(position, value)
        return {self.identifier: str(len(values))}

    def prepareRequestValue(self, values):
        count = int(values.get(self.identifier, '0'))
        remove_something = self.identifier + '.remove' in values
        for position in range(0, count):
            value_marker = (self.identifier, position,)
            value_present = '%s.present.%d' % value_marker in values
            if not value_present:
                continue
            value_selected = '%s.checked.%d' % value_marker in values
            if remove_something and value_selected:
                continue
            self.newValueWidget(position, None)
        if self.identifier + '.add' in values:
            self.newValueWidget(count, None)
            values[self.identifier] = str(count + 1)
        return values

    def update(self):
        super(MultiGenericFieldWidget, self).update()
        if not int(self.inputValue()):
            self.allowRemove = False
        self.valueWidgets.update()

# For collection of objects, generate a different widget (with a table)

class MultiObjectFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ICollectionSchemaField, ObjectSchemaField, Interface, Interface)

    def getFields(self):
        return self.valueField.objectFields


class MultiGenericWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionSchemaField, Interface, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiGenericWidgetExtractor, self).__init__(field, form, request)
        self.valueField = value_field

    def extract(self):
        value = self.request.form.get(self.identifier, NO_VALUE)
        if value is not NO_VALUE:
            try:
                value = int(value)
            except ValueError:
                return (None, u"Invalid internal input")
            collectedValues = []
            for position in range(0, int(value)):
                value_present = '%s.present.%d' % (
                    self.identifier, position) in self.request.form
                if not value_present:
                    # This value have been removed
                    continue
                field = self.valueField.clone(new_identifier=str(position))
                form = cloneFormData(self.form, prefix=self.identifier)
                data, errors = form.extractData(Fields(field))
                if errors is not None:
                    return (None, errors)
                collectedValues.append(data[field.identifier])
            value = self.component.collectionType(collectedValues)
        return (value, None)


# Multi-Choice widget

class MultiChoiceFieldWidget(ChoiceFieldWidget):
    grok.adapts(ICollectionSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceFieldWidget, self).__init__(field, form, request)
        self.source = value_field

    def prepareContentValue(self, value):
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
        value, errors = super(MultiChoiceWidgetExtractor, self).extract()
        if value is not NO_VALUE and errors is None:
            choices = self.source.getChoices(self.form.context)
            try:
                value = self.component.collectionType(
                    [choices.getTermByToken(t).value for t in value])
            except LookupError:
                return (None, u'Invalid value')
        return (value, errors)
