import zeam.form.ztk.compat
from zeam.form.base.fields import Field
from zeam.form.base.widgets import FieldWidget
from zeam.form.ztk.fields import registerSchemaField
from zeam.form.base.markers import Marker, NO_VALUE

from grokcore import component as grok
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

_ = MessageFactory("zeam.form.base")
rfc822_specials = '()<>@,;:\\"[]'

def isMailAddress(addr):
    """Returns True if the email address is valid and False if not."""

    # First we validate the name portion (name@domain)
    c = 0
    while c < len(addr):
        if addr[c] == '@':
            break
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1

    # check whether we have any input and that the name did not end with a dot
    if not c or addr[c - 1] == '.':
        return False

    # check also starting and ending dots in (name@domain)
    if addr.startswith('.') or addr.endswith('.'):
        return False

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    # Ensure that the domain is not empty (name@)
    if domain >= len(addr):
        return False
    count = 0
    while c < len(addr):
        # Make sure that domain does not end with a dot or has two dots in a row
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.':
                return False
            count = count + 1
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1
    if count >= 1:
        return True
    return False


class EmailField(Field):

    def __init__(self, title,
                 minLength=0,
                 maxLength=None,
                 **options):
        super(EmailField, self).__init__(title, **options)
        self.minLength = minLength
        self.maxLength = maxLength

    def isEmpty(self, value):
        return value is NO_VALUE or not len(value)

    def validate(self, value, form):
        error = super(EmailField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker) and len(value):
            assert isinstance(value, zeam.form.ztk.compat.string_types)
            if not isMailAddress(value):
                return _(u"This email is not valid.")
            if self.minLength and len(value) < self.minLength:
                return _(u"This email is too short.")
            if self.maxLength and len(value) > self.maxLength:
                return _(u"This email is too long.")
        return None


class EmailWidget(FieldWidget):
    grok.adapts(EmailField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-email']
    defaultHtmlAttributes = set(['readonly', 'required', 'autocomplete',
                                 'maxlength', 'pattern', 'placeholder',
                                 'size', 'style'])


class EmailDisplayWidget(FieldWidget):
    grok.adapts(EmailField, Interface, Interface)
    grok.name('display')


def EmailSchemaFactory(schema):
    field = EmailField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        minLength=schema.min_length,
        maxLength=schema.max_length,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultValue=schema.default or NO_VALUE)
    return field


try:
    from z3c.schema.email.interfaces import IRFC822MailAddress

    def register():
        registerSchemaField(EmailSchemaFactory, IRFC822MailAddress)

except ImportError:

    def register():
        pass
