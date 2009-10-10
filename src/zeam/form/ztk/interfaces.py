
from zeam.form.base import interfaces


class ISchemaField(interfaces.IField):
    """This is a field for zope schema field.
    """

    def setContentValue(content, value):
        """Set the value on the content.
        """

    def fromUnicode(value):
        """This convert a value from a unicode string (or not).
        """
