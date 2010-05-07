# -*- coding: utf-8 -*-

from zeam.form.base.markers import NO_VALUE
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import (
    SchemaField, registerSchemaField, SchemaFieldWidget)

from zope import component
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


class ChoiceSchemaField(SchemaField):
    """A choice field.
    """

    def __init__(self, field):
        super(ChoiceSchemaField, self).__init__(field)
        self.__source = None
        self.__source_name = None
        if field.source is not None:
            self.__source = field.source
        elif isinstance(field.vocabularyName, str):
            # We delay the lookup of the vocabulary, to be sure it
            # have been registered.
            self.__source = None
            self.__source_name = field.vocabularyName

    @property
    def source(self):
        if self.__source is None:
            self.__source = component.getUtility(
                schema_interfaces.IVocabularyFactory, name=self.__source_name)
        return self.__source

    def getChoices(self, context):
        source = self.source
        if (schema_interfaces.IContextSourceBinder.providedBy(source) or
            schema_interfaces.IVocabularyFactory.providedBy(source)):
            source = source(context)
        assert schema_interfaces.IVocabularyTokenized.providedBy(source)
        return source


registerSchemaField(ChoiceSchemaField, schema_interfaces.IChoice)


class ChoiceFieldWidget(SchemaFieldWidget):
    grok.adapts(ChoiceSchemaField, Interface, Interface)

    def __init__(self, field, form, request):
        super(ChoiceFieldWidget, self).__init__(field, form, request)
        self.source = field
        self.__choices = None

    def valueToUnicode(self, value):
        term = self.choices().getTerm(value)
        return term.token

    def choices(self):
        if self.__choices is not None:
            return self.__choices
        # self.source is used instead of self.component in order to be
        # able to override it in subclasses.
        self.__choices = self.source.getChoices(self.form.context)
        return self.__choices


class ChoiceWidgetExtractor(WidgetExtractor):
    grok.adapts(ChoiceSchemaField, Interface, Interface)

    def extract(self):
        value, error = super(ChoiceWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            choices = self.component.getChoices(self.form.context)
            try:
                value = choices.getTermByToken(value).value
            except LookupError:
                return (None, u'Invalid value')
        return (value, error)
