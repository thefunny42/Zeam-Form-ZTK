
from zeam.form.base import interfaces


class ISchemaField(interfaces.IField):
    """This is a field for zope schema field.
    """

    def fromUnicode(value):
        """This convert a value from a unicode string (or not).
        """
