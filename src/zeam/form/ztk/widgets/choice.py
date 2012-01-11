# -*- coding: utf-8 -*-

from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import (
    SchemaField, registerSchemaField, SchemaFieldWidget)

from zope import component
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


def register():
    registerSchemaField(ChoiceSchemaField, schema_interfaces.IChoice)


class ChoiceSchemaField(SchemaField):
    """A choice field.
    """

    def __init__(self, field):
        super(ChoiceSchemaField, self).__init__(field)
        self._source = None
        self._source_name = None
        self._custom = None    # The field can have a custom source.
        if field.source is not None:
            self._source = field.source
        elif isinstance(field.vocabularyName, str):
            # We delay the lookup of the vocabulary, to be sure it
            # have been registered.
            self._source_name = field.vocabularyName

    @apply
    def source():

        def getter(self):
            if self._source is None:
                if self._custom is not None:
                    self._source = self._custom
                else:
                    self._source = component.getUtility(
                        schema_interfaces.IVocabularyFactory,
                        name=self._source_name)
            return self._source

        def setter(self, source):
            self._custom = source

        return property(getter, setter)

    def getChoices(self, form):
        source = self.source
        if (schema_interfaces.IContextSourceBinder.providedBy(source) or
            schema_interfaces.IVocabularyFactory.providedBy(source)):
            source = source(form.context)
        elif callable(source):
            source = source(form)
        # If that's custom, we need to re-inject this in zope.schema
        # to get it right.
        self._field.vocabulary = source
        assert schema_interfaces.IVocabularyTokenized.providedBy(source)
        return source


class ChoiceFieldWidget(SchemaFieldWidget):
    grok.adapts(ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, form, request):
        super(ChoiceFieldWidget, self).__init__(field, form, request)
        self.source = field
        self._choices = None

    def lookupTerm(self, value):
        choices = self.choices()
        try:
            return choices.getTerm(value)
        except LookupError:
            # the stored value is invalid. fallback on the default one.
            default = self.component.getDefaultValue(self.form)
            if default is not NO_VALUE:
                return choices.getTerm(default)
        return None

    def valueToUnicode(self, value):
        term = self.lookupTerm(value)
        if term is not None:
            return term.token
        return u''

    def choices(self):
        if self._choices is not None:
            return self._choices
        # self.source is used instead of self.component in order to be
        # able to override it in subclasses.
        self._choices = self.source.getChoices(self.form)
        return self._choices


class ChoiceDisplayWidget(ChoiceFieldWidget):
    grok.name('display')

    def valueToUnicode(self, value):
        term = self.lookupTerm(value)
        if term is not None:
            return term.title
        return u''


class ChoiceWidgetExtractor(WidgetExtractor):
    grok.adapts(ChoiceSchemaField, Interface, Interface)

    def extract(self):
        value, error = super(ChoiceWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            choices = self.component.getChoices(self.form)
            try:
                value = choices.getTermByToken(value).value
            except LookupError:
                return (None, u'Invalid value')
        return (value, error)


# Radio Widget

class RadioFieldWidget(ChoiceFieldWidget):
    grok.adapts(ChoiceSchemaField, Interface, Interface)
    grok.name('radio')

    def renderableChoices(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for i, choice in enumerate(self.choices()):
            yield {'token': choice.token,
                   'title': choice.title or choice.token,
                   'checked': choice.token == current and 'checked' or None,
                   'id': base_id + '-' + str(i)}
