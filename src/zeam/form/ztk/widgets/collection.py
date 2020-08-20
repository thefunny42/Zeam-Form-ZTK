# -*- coding: utf-8 -*-

try:
    import hashlib
    md5hash = lambda s: hashlib.md5(s).hexdigest()
except ImportError:
    import md5
    md5hash = lambda s: md5.new(s).hexdigest()

try:
    # If you have the fanstatic extra, add support to include widget JS
    import fanstatic
    import js.jquery
    import zeam.jsontemplate

    library = fanstatic.Library('zeam.form.ztk.widgets', 'static')
    collection = fanstatic.Resource(
        library, 'collection.js', depends=[js.jquery.jquery,
                                           zeam.jsontemplate.jsontemplate])
    requireCollectionResources = collection.need
except ImportError:
    class Library(object):
        name = ""

        def init_library_nr(self):
            pass

        @property
        def library_nr(self):
            return 20000

        @property
        def known_assets(self):
            return []


    library = Library()
    requireCollectionResources = lambda: None

from zeam.form.base.datamanager import NoneDataManager
from zeam.form.base.errors import Errors, Error
from zeam.form.base.fields import Fields
from zeam.form.base.markers import Marker
from zeam.form.base.form import cloneFormData
from zeam.form.base.interfaces import IField, IWidget, IWidgetExtractor
from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor, FieldWidget, Widgets
from zeam.form.ztk.fields import Field, registerSchemaField
from zeam.form.ztk.interfaces import ICollectionField, IListField
from zeam.form.ztk.widgets.choice import ChoiceField, ChoiceFieldWidget
from zeam.form.ztk.widgets.object import ObjectField

from grokcore import component as grok
from zope import component
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implementer
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


@implementer(ICollectionField)
class CollectionField(Field):
    """A collection field.
    """
    collectionType = list
    allowAdding = True
    allowRemove = True
    inlineValidation = False

    def __init__(self, title,
                 valueField=None,
                 minLength=0,
                 maxLength=None,
                 **options):
        super(CollectionField, self).__init__(title, **options)
        self._valueField = IField(valueField, None)
        self.minLength = minLength
        self.maxLength = maxLength

    @property
    def valueField(self):
        return self._valueField

    def validate(self, value, form):
        error = super(CollectionField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            assert isinstance(value, self.collectionType)
            if self.minLength and len(value) < self.minLength:
                return _(u"There are too few items.")
            if self.maxLength and len(value) > self.maxLength:
                return _(u"There are too many items.")
        return None

    def isEmpty(self, value):
        return value is NO_VALUE or not len(value)


# BBB
CollectionSchemaField = CollectionField


@implementer(IListField)
class ListField(CollectionField):
    """A list field
    """
    collectionType = list
    allowOrdering = True


# BBB
ListSchemaField = ListField


class SetField(CollectionField):
    """A set field
    """
    collectionType = set


# BBB
SetSchemaField = SetField


class TupleField(CollectionField):
    """A tuple field.
    """
    collectionType = tuple


# BBB
TupleSchemaField = TupleField


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
    adapts=(ICollectionField, Interface, Interface),
    provides=IWidget,
    name='input')

grok.global_adapter(
    newCollectionWidgetFactory(mode='input-list'),
    adapts=(ICollectionField, Interface, Interface),
    provides=IWidget,
    name='input-list')

grok.global_adapter(
    newCollectionWidgetFactory(mode='display'),
    adapts=(ICollectionField, Interface, Interface),
    provides=IWidget,
    name='display')

grok.global_adapter(
    newCollectionWidgetFactory(interface=IWidgetExtractor),
    adapts=(ICollectionField, Interface, Interface),
    provides=IWidgetExtractor)


class MultiGenericFieldWidget(FieldWidget):
    grok.adapts(ICollectionField, Interface, Interface, Interface)

    allowAdding = True
    allowRemove = True
    inlineValidation = False

    def __init__(self, field, value_field, form, request):
        super(MultiGenericFieldWidget, self).__init__(field, form, request)
        self.allowAdding = field.allowAdding
        self.allowRemove = field.allowRemove
        self.inlineValidation = field.inlineValidation
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
        return form.widgetFactory.widget(field)

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

    def prepareRequestValue(self, values, extractor):
        value_count = 0
        errors = None
        identifier_count = int(values.get(self.identifier, '0'))
        remove_something = self.identifier + '.remove' in values
        add_something = self.identifier + '.add' in values

        if self.inlineValidation:
            # If inlineValidation is on, and we removed or added
            # something, we extract this field to get the
            # validation messages right away (if the user clicked
            # on add or remove, he cannot have clicked on an
            # action button)
            if add_something or remove_something:
                ignored, errors = extractor.extract()
                if errors:
                    self.form.errors.append(errors)

        for position in range(0, identifier_count):
            value_marker = (self.identifier, position,)
            value_present = '%s.present.%d' % value_marker in values
            if not value_present:
                continue
            value_identifier = '%s.field.%d' % value_marker
            value_selected = '%s.checked.%d' % value_marker in values
            if remove_something and value_selected:
                if errors and value_identifier in errors:
                    # If the field have an error, remove it
                    del errors[value_identifier]
                continue
            # We need to provide the widget error now, but cannot set
            # all of them on the form now, as we might remove them
            # with delete
            self.addValueWidget(position, None)
            value_count += 1
        if (add_something or
            (self.allowAdding and self.required and not value_count)):
            self.addValueWidget(identifier_count, None)
            value_count += 1
            values[self.identifier] = str(identifier_count + 1)
        if value_count:
            self.haveValues = True
        if errors:
            if len(errors) > 1:
                self.form.errors.append(
                    Error(_(u"There were errors."), self.form.prefix))
            else:
                # If no errors  are left, remove from the form (top level error)
                del self.form.errors[self.identifier]
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
        requireCollectionResources()

        self.jsonAddIdentifier = None
        self.jsonAddTemplate = None
        self.includeEmptyMessage = self.allowRemove
        if self.allowAdding:
            self.jsonAddIdentifier = 'id' + md5hash(
                self.identifier.encode('utf-8'))
            widgets = Widgets()
            widgets.append(self.createValueWidget(
                    '{' + self.jsonAddIdentifier + '}', None))
            widgets.update()
            self.jsonAddTemplate = list(widgets)[0]


class ListGenericFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ListField, Interface, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(ListGenericFieldWidget, self).__init__(
            field, value_field, form, request)
        self.allowOrdering = field.allowOrdering


class MultiGenericDisplayFieldWidget(MultiGenericFieldWidget):
    grok.name('display')


# For collection of objects, generate a different widget (with a table)

class MultiObjectFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ICollectionField, ObjectField, Interface, Interface)

    def getFields(self):
        return self.valueField.objectFields


class ListObjectFieldWidget(MultiObjectFieldWidget):
    grok.adapts(ListField, ObjectField, Interface, Interface)

    def __init__(self, field, value_field, form, request):
        super(ListObjectFieldWidget, self).__init__(
            field, value_field, form, request)
        self.allowOrdering = field.allowOrdering


# Still make possible to have the non-table implementation

class RegularMultiObjectFieldWidget(MultiGenericFieldWidget):
    grok.adapts(ICollectionField, ObjectField, Interface, Interface)
    grok.name('input-list')


class RegularListObjectFieldWidget(ListGenericFieldWidget):
    grok.adapts(ListField, ObjectField, Interface, Interface)
    grok.name('input-list')


class MultiGenericWidgetExtractor(WidgetExtractor):
    grok.adapts(ICollectionField, Interface, Interface, Interface)

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
    grok.adapts(SetField, ChoiceField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-multichoice']

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
    adapts=(ICollectionField, Interface, Interface),
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
    grok.adapts(SetField, ChoiceField, Interface, Interface)

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
            choices = self.source.getChoices(self.form)
            try:
                if not isinstance(value, list):
                    value = [value]
                value = self.component.collectionType(
                    [choices.getTermByToken(t).value for t in value])
            except LookupError:
                return (None, _(u'The selected value is not available.'))
        return (value, errors)


def makeCollectionSchemaFactory(factory):

    def CollectionSchemaFactory(schema):
        field = factory(
            schema.title or None,
            identifier=schema.__name__,
            description=schema.description,
            required=schema.required,
            readonly=schema.readonly,
            minLength=schema.min_length,
            maxLength=schema.max_length,
            valueField=schema.value_type,
            interface=schema.interface,
            constrainValue=schema.constraint,
            defaultFactory=schema.defaultFactory,
            defaultValue=schema.__dict__['default'] or NO_VALUE)
        return field

    return CollectionSchemaFactory


def register():
    registerSchemaField(
        makeCollectionSchemaFactory(CollectionField),
        schema_interfaces.ICollection)
    registerSchemaField(
        makeCollectionSchemaFactory(ListField),
        schema_interfaces.IList)
    registerSchemaField(
        makeCollectionSchemaFactory(SetField),
        schema_interfaces.ISet)
    registerSchemaField(
        makeCollectionSchemaFactory(TupleField),
        schema_interfaces.ITuple)
