# -*- coding: utf-8 -*-

from zeam.form.base.interfaces import IFieldExtractionValueSetting
from zeam.form.base.markers import Marker, NO_VALUE
from zeam.form.base.widgets import FieldWidget, FieldWidgetExtractor
from zeam.form.ztk.fields import Field, registerSchemaField

from grokcore import component as grok
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("zeam.form.base")


class IntegerField(Field):
    """A integer field.
    """

    def __init__(self, title,
                 min=None,
                 max=None,
                 **options):
        # We pass min and max to Field to have them in htmlAttributes as well
        super(IntegerField, self).__init__(title, min=min, max=max, **options)
        self.min = min
        self.max = max

    def validate(self, value, form):
        error = super(IntegerField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            assert isinstance(value, (int, float))
            if self.min is not None and value < self.min:
                return _(u"This number is too small.")
            if self.max is not None and value > self.max:
                return _(u"This number is too big.")
        return None

# BBB
IntSchemaField = IntegerField


class IntegerFieldWidgetExtractor(FieldWidgetExtractor):
    grok.adapts(IntegerField, IFieldExtractionValueSetting, Interface)
    valueType = int
    failedMessage = _(u"This number is not a valid whole number.")

    def extract(self):
        value, error = super(IntegerFieldWidgetExtractor, self).extract()
        if error:
            return (value, error)
        if value is not NO_VALUE and len(value):
            try:
                value = self.valueType(value)
            except (ValueError, TypeError):
                return (NO_VALUE, self.failedMessage)
            return (value, None)
        return (NO_VALUE, None)


class FloatField(IntegerField):
    """A float field.
    """


# BBB
FloatSchemaField = FloatField


class CurrencyField(FloatField):
    """ A currency field.
    """

    def __init__(self, min=None,
                       max=None,
                       symbol=u'€',
                       thousandsSeparator=u',',
                       decimalSeparator=u'.',
                       symbolPrecedes=False,
                       symbolSpaceSepartor=True,
                       fracDigits=2,
                       positiveSign=u'',
                       negativeSign=u'-',
                       signPrecedes=True,
                       **options):
        super(CurrencyField, self).__init__(max=max, min=min, **options)
        self.symbol = symbol
        self.thousandsSeparator = thousandsSeparator
        self.decimalSeparator = decimalSeparator
        self.symbolPrecedes = symbolPrecedes
        self.symbolSpaceSepartor = symbolSpaceSepartor
        self.fracDigits = fracDigits
        self.positiveSign = positiveSign
        self.negativeSign = negativeSign
        self.signPrecedes = signPrecedes


class FloatFieldWidgetExtractor(IntegerFieldWidgetExtractor):
    grok.adapts(FloatField, IFieldExtractionValueSetting, Interface)
    valueType = float
    failedMessage = _(u"This number is not a valid decimal number.")


class NumberWidget(FieldWidget):
    grok.adapts(IntegerField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-number']
    defaultHtmlAttributes = set(['readonly', 'required', 'autocomplete',
                                 'max', 'min', 'setup', 'placeholder',
                                 'style'])


class CurrencyDisplayWidget(FieldWidget):
    grok.adapts(CurrencyField, Interface, Interface)
    grok.name('display')

    defaultHtmlClass = ['field', 'field-currency']

    def valueToUnicode(self, value):
        return self.formatHtmlCurrency(value)

    def formatHtmlCurrency(self, value):
        string_value = ("%%.0%df" % self.component.fracDigits) % abs(value)
        integer_part, decimal_part = string_value.split('.')
        digits = list(integer_part)
        chars = []
        count = 0
        while digits:
            digit = digits.pop()
            chars.append(digit)
            count += 1
            if count % 3 == 0 and len(digits):
                chars.append(self.component.thousandsSeparator)
        integer_part = "".join(reversed(chars))
        buf = u''
        if self.component.symbolPrecedes:
            buf += self.component.symbol
            if self.component.symbolSpaceSepartor:
                buf += '&nbsp;'
        if value >= 0:
            buf += self.component.positiveSign
        else:
            buf += self.component.negativeSign
        buf += integer_part + self.component.decimalSeparator + decimal_part
        if not self.component.symbolPrecedes:
            if self.component.symbolSpaceSepartor:
                buf += '&nbsp;'
            buf += self.component.symbol
        return buf


def IntegerSchemaFactory(schema):
    field = IntegerField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        min=schema.min,
        max=schema.max,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.__dict__['default'] or NO_VALUE)
    return field


def FloatSchemaFactory(schema):
    field = FloatField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        min=schema.min,
        max=schema.max,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.__dict__['default'] or NO_VALUE)
    return field


def register():
    registerSchemaField(FloatSchemaFactory, schema_interfaces.IFloat)
    registerSchemaField(IntegerSchemaFactory, schema_interfaces.IInt)
