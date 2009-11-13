
from zeam.form.base.widgets import FieldWidget, WidgetExtractor
from zeam.form.base.markers import NO_VALUE
from zeam.form.ztk.fields import SchemaField, registerSchemaField

from zope.schema import interfaces as schema_interfaces
from zope.interface import Interface

from grokcore import component as grok


class ChoiceSchemaField(SchemaField):

    def __init__(self, field):
        super(ChoiceSchemaField, self).__init__(field)
        if field.source is not None:
            self.__source = field.source
        elif isinstance(field.vocabulary, str):
            self.__source = component.getUtility(
                schema_interfaces.IVocabulary, name=field.vocabulary)

    @property
    def source(self):
        return self.__source


registerSchemaField(ChoiceSchemaField, schema_interfaces.IChoice)


class ChoiceFieldWidget(FieldWidget):
    grok.adapts(ChoiceSchemaField, Interface, Interface)

    def __init__(self, *args):
        super(ChoiceFieldWidget, self).__init__(*args)
        self.__choices = None

    def valueToUnicode(self, value):
        term = self.choices().getTerm(value)
        return term.token

    def choices(self):
        if self.__choices is not None:
            return self.__choices
        source = self.component.source
        if (schema_interfaces.IContextSourceBinder.providedBy(source) or
            schema_interfaces.IVocabularyFactory.providedBy(source)):
            source = source(self.form.getContent())
        assert schema_interfaces.IVocabularyTokenized.providedBy(source)
        self.__choices = source
        return self.__choices
