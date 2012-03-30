# -*- coding: utf-8 -*-

from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.interfaces import IFormSourceBinder
from zeam.form.ztk.fields import (
    SchemaField, registerSchemaField, SchemaFieldWidget)

from zope import component
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
from zope.schema.interfaces import IVocabularyTokenized, IVocabularyFactory
from zope.schema.interfaces import IContextSourceBinder

from grokcore import component as grok


def register():
    registerSchemaField(ChoiceSchemaField, schema_interfaces.IChoice)


class ChoiceSchemaField(SchemaField):
    """A choice field.
    """

    def __init__(self, field):
        super(ChoiceSchemaField, self).__init__(field)
        self._source = None
        self._factory = None    # The field can have a custom factory.
        self._factory_name = None
        if field.source is not None:
            if IVocabularyTokenized.providedBy(field.source):
                self._source = field.source
            else:
                self._factory = field.source
        elif isinstance(field.vocabularyName, str):
            # We delay the lookup of the vocabulary, to be sure it
            # have been registered.
            self._factory_name = field.vocabularyName

    @apply
    def factory():

        def getter(self):
            if self._factory is None:
                if self._factory_name is not None:
                    self._factory = component.getUtility(
                        schema_interfaces.IVocabularyFactory,
                        name=self._factory_name)
            return self._factory

        def setter(self, factory):
            if isinstance(factory, str):
                self._factory_name = factory
                self._factory = None
            else:
                self._factory_name = None
                self._factory = factory
            self._source = None

        return property(getter, setter)

    @apply
    def source():

        def getter(self):
            return self._source

        def setter(self, source):
            if IVocabularyTokenized.providedBy(source):
                # If that's custom, we need to re-inject this in zope.schema
                # to get validation working properly.
                self._source = source
                self._field.vocabulary = source
            else:
                # This is a factory.
                self.factory = source

        return property(getter, setter)

    def getChoices(self, form, reset=False):
        source = self.source
        if source is None or reset:
            factory = self.factory
            assert factory is not None, \
                "No vocabulary source available."
            if (IContextSourceBinder.providedBy(factory) or
                IVocabularyFactory.providedBy(factory)):
                source = factory(form.context)
            elif IFormSourceBinder.providedBy(factory):
                source = factory(form)
            assert IVocabularyTokenized.providedBy(source), \
                "No valid vocabulary available, %s is not valid for %s" % (
                source, self)
            self._field.vocabulary = source
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
