# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import NoneDataManager
from zeam.form.base.interfaces import IField, IWidget, IWidgetExtractor
from zeam.form.base.form import cloneFormData
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
        remove_something = self.identifier + '.remove' in self.request.form
        for position in range(0, count):
            value_selected = '%s.field.%d.checked' % (
                self.identifier, position) in self.request.form
            if remove_something and value_selected:
                print 'Remove %d' % position
                continue
            self.newValueWidget(position, None)
        if self.identifier + '.add' in self.request.form:
            self.newValueWidget(count, None)
            values[self.identifier] = str(count)
        return values

    def update(self):
        super(MultiGenericFieldWidget, self).update()
        if not int(self.inputValue()):
            self.allowRemove = False
        self.valueWidgets.update()


class MultiGenericWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionSchemaField, Interface, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiGenericWidgetExtractor, self).__init__(field, form, request)
        self.source = value_field

    def extract(self):
        # Not implemented yet
        return (NO_VALUE, None)


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
        value, error = super(MultiChoiceWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            choices = self.source.getChoices(self.form.context)
            try:
                value = self.component.collectionType(
                    [choices.getTermByToken(t).value for t in value])
            except LookupError:
                return (None, u'Invalid value')
        return (value, error)
