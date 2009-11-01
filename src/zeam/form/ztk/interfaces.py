
from zope import interface

from zeam.form.base.interfaces import IField, IZeamFormBaseAPI


class ISchemaField(IField):
    """This is a field for zope schema field.
    """

    def setContentValue(value, content):
        """Set the value on the content.
        """

    def fromUnicode(value):
        """This convert a value from a unicode string (or not).
        """


class IZeamFormZTKAPI(IZeamFormBaseAPI):
    """API exported by zeam.form.ztk.
    """

    AddAction = interface.Attribute(
        u"Action to add a new content to one other")
    EditAction = interface.Attribute(
        u"Action to edit the values of a content")
    CancelAction = interface.Attribute(
        u"Action to cancel the submission of the form")
