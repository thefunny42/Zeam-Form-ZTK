# -*- coding: utf-8 -*-

try:
    import hashlib
    md5hash = lambda s: hashlib.md5(s).hexdigest()
except ImportError:
    import md5
    md5hash = lambda s: md5.new(s).hexdigest()

from zeam.form.base.datamanager import NoneDataManager
from zeam.form.base.errors import Errors
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
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok

_ = MessageFactory("zeam.form.base")



def register():
    registerSchemaField(CollectionSchemaField, schema_interfaces.ICollection)
    registerSchemaField(ListSchemaField, schema_interfaces.IList)
    registerSchemaField(SetSchemaField, schema_interfaces.ISet)
    registerSchemaField(TupleSchemaField, schema_interfaces.ITuple)


class CollectionSchemaField(SchemaField):
    """A collection field.
    """
    grok.implements(ICollectionSchemaField)

    collectionType = list
    allowAdding = True
    allowRemove = True

    def __init__(self, field):
        super(CollectionSchemaField, self).__init__(field)
        self.__value_field = IField(self._field.value_type)

    @property
    def valueField(self):
        return self.__value_field

    def isEmpty(self, value):
        return value is NO_VALUE or not len(value)


class ListSchemaField(CollectionSchemaField):
    """A list field
    """
    collectionType = list
    allowOrdering = True


class SetSchemaField(CollectionSchemaField):
    """A set field
    """
    collectionType = set


class TupleSchemaField(CollectionSchemaField):
    """A tuple field.
    """
    collectionType = tuple


def newCollectionWidgetFactory(mode=u"", interface=IWidget):
    def collectionWidgetFactory(field, form, request):
        """A widget of a collection is a bit advanced. We have to adapt
        the sub-type of the field as well.
        """
        widget = component.getMultiAdapter(
            (field, field.valueField, form, request), interface, name=mode)
        return widget
    return collectionWidgetFactory


grok.global_adapter(
    newCollectionWidgetFactory(mode='input'),
    adapts=(ICollectionSchemaField, Interface, Interface),
    provides=IWidget,
    name='input')

grok.global_adapter(
    newCollectionWidgetFactory(mode='list'),
    adapts=(ICollectionSchemaField, Interface, Interface),
    provides=IWidget,
    name='list')

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
        self.allowAdding = field.allowAdding
        self.allowRemove = field.allowRemove
        self.valueField = value_field
        self.valueWidgets = Widgets()
        self.haveValues = False

    def createValueWidget(self, new_identifier, value):
        field = self.valueField.clone(new_identifier=str(new_identifier))
        form = cloneFormData(self.form, prefix=self.identifier)
        if value is not None:
            form.ignoreContent = False
            form.setContentData(NoneDataManager(value))
        else:
            form.ignoreRequest = False
            form.ignoreContent = True
        return createWidget(field, form, self.request)

    def addValueWidget(self, new_identifier, value):
        widget = self.createValueWidget(new_identifier, value)
        if widget is not None:
            self.valueWidgets.append(widget)
        return widget

    def prepareContentValue(self, values):
        count = 0
        if values is not NO_VALUE:
            for position, value in enumerate(values):
                # Create new widgets for each value
                self.addValueWidget(position, value)
            count += len(values)
        if self.allowAdding and self.required and not count:
            self.addValueWidget(count, None)
            count += 1
        if count:
            self.haveValues = True
        return {self.identifier: str(count)}

    def prepareRequestValue(self, values):
        value_count = 0
        identifier_count = int(values.get(self.identifier, '0'))
        remove_something = self.identifier + '.remove' in values
        for position in range(0, identifier_count):
            value_marker = (self.identifier, position,)
            value_present = '%s.present.%d' % value_marker in values
            if not value_present:
                continue
            value_selected = '%s.checked.%d' % value_marker in values
            if remove_something and value_selected:
                continue
            self.addValueWidget(position, None)
            value_count += 1
        if ((self.identifier + '.add' in values) or
            (self.allowAdding and self.required and not value_count)):
            self.addValueWidget(identifier_count, None)
            value_count += 1
            values[self.identifier] = str(identifier_count + 1)
        if value_count:
            self.haveValues = True
        return values

    @property
    def jsonTemplateWidget(self):
        widgets = Widgets()
        widgets.append(self.createValueWidget('{identifier}', None))
        widgets.update()
        return list(widgets)[0]

    def update(self):
        super(MultiGenericFieldWidget, self).update()
        self.valueWidgets.update()

        self.jsonAddIdentifier = None
        self.jsonAddTemplate = None
        self.includeEmptyMessage = self.allowRemove
        if self.allowAdding:
            self.jsonAddIdentifier = 'id' + md5hash(self.identifier)
            widgets = Widgets()
            widgets.append(self.createValueWidget(
                   '{' + self.jsonAddIdentifier + '}', None))
            widgets.update()
            self.jsonAddTemplate = list(widgets)[0]


class ListGenericFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ListSchemaField, Interface, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(ListGenericFieldWidget, self).__init__(
            field, value_field, form, request)
        self.allowOrdering = field.allowOrdering


class MultiGenericDisplayFieldWidget(MultiGenericFieldWidget):
    grok.name('display')


# For collection of objects, generate a different widget (with a table)

class MultiObjectFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ICollectionSchemaField, ObjectSchemaField, Interface, Interface)

    def getFields(self):
        return self.valueField.objectFields


class ListObjectFieldWidget(MultiObjectFieldWidget):
    grok.adapts(ListSchemaField, ObjectSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(ListObjectFieldWidget, self).__init__(
            field, value_field, form, request)
        self.allowOrdering = field.allowOrdering

# Still make possible to have the non-table implementation

class RegularMultiObjectFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ICollectionSchemaField, ObjectSchemaField, Interface, Interface)
    grok.name('list')


class RegularListObjectFieldWidget(ListGenericFieldWidget):
    grok.adapts(ListSchemaField, ObjectSchemaField, Interface, Interface)
    grok.name('list')


class MultiGenericWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionSchemaField, Interface, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiGenericWidgetExtractor, self).__init__(
            field, form, request)
        self.valueField = value_field

    def extract(self):
        value = self.request.form.get(self.identifier, NO_VALUE)
        if value is not NO_VALUE:
            try:
                value = int(value)
            except ValueError:
                return (None, u"Invalid internal input")
            collectedValues = []
            collectedErrors = Errors(identifier=self.identifier)
            for position in range(0, value):
                value_present = '%s.present.%d' % (
                    self.identifier, position) in self.request.form
                if not value_present:
                    # This value have been removed
                    continue
                field = self.valueField.clone(new_identifier=str(position))
                form = cloneFormData(self.form, prefix=self.identifier)
                data, errors = form.extractData(Fields(field))
                if errors:
                    collectedErrors.extend(errors)
                else:
                    collectedValues.append(data[field.identifier])
            if collectedErrors:
                return (None, collectedErrors)
            value = self.component.collectionType(collectedValues)
        return (value, None)


# Multi-Choice widget

class MultiChoiceFieldWidget(ChoiceFieldWidget):
    grok.adapts(SetSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceFieldWidget, self).__init__(field, form, request)
        self.source = value_field

    def prepareContentValue(self, value):
        form_value = []
        if value is NO_VALUE:
            return {self.identifier: form_value}
        choices = self.choices()
        for entry in value:
            try:
                term = choices.getTerm(entry)
                form_value.append(term.token)
            except LookupError:
                pass
        return {self.identifier: form_value}

    def renderableChoice(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for i, choice in enumerate(self.choices()):
            yield {'token': choice.token,
                   'title': choice.title,
                   'checked': choice.token in current,
                   'id': base_id + '-' + str(i)}


grok.global_adapter(
    newCollectionWidgetFactory(mode='multiselect'),
    adapts=(ICollectionSchemaField, Interface, Interface),
    provides=IWidget,
    name='multiselect')


class MultiSelectFieldWidget(MultiChoiceFieldWidget):
    grok.name('multiselect')


class MultiChoiceDisplayFieldWidget(MultiChoiceFieldWidget):
    grok.name('display')

    def renderableChoice(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for i, choice in enumerate(self.choices()):
            if choice.token in current:
                yield {'title': choice.title,
                       'id': base_id + '-' + str(i)}


class MultiChoiceWidgetExtractor(WidgetExtractor):
    grok.adapts(SetSchemaField, ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(MultiChoiceWidgetExtractor, self).__init__(field, form, request)
        self.source = value_field

    def extract(self):
        value, errors = super(MultiChoiceWidgetExtractor, self).extract()
        if errors is None:
            is_present = self.request.form.get(
                self.identifier + '.present', NO_VALUE)
            if is_present is NO_VALUE:
                # Not in the request
                return (NO_VALUE, None)
            if value is NO_VALUE:
                # Nothing selected
                return (self.component.collectionType(), None)
            choices = self.source.getChoices(self.form.context)
            try:
                if not isinstance(value, list):
                    value = [value]
                value = self.component.collectionType(
                    [choices.getTermByToken(t).value for t in value])
            except LookupError:
                return (None, _(u'The selected value is not available.'))
        return (value, errors)
