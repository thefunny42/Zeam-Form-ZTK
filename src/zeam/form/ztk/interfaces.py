# -*- coding: utf-8 -*-

from zope import interface
from zeam.form.base.interfaces import IField, IZeamFormBaseAPI


class ISchemaField(IField):
    """This is a field for zope schema field.
    """

    def fromUnicode(value):
        """This convert a value from a unicode string (or not).
        """


class ICollectionSchemaField(ISchemaField):
    """This is a field for zope schema collection field. It is defined
    in order to be able to have a generic behavior on collections.
    """
    collectionType = interface.Attribute(
        u"Python type represented by this collection (like set, list...)")
    valueField = interface.Attribute(
        u"Field corresponding to the value type contained in the collection")


class IObjectSchemaField(ISchemaField):
    """This field is mapped to the zope.schema Object schema field.
    """
    objectFactory = interface.Attribute(
        u"Default factory used to create new objects for the field")
    objectSchema = interface.Attribute(
        u"Zope Interface that should be implemented by the object")
    objectFields = interface.Attribute(
        u"Zeam fields for the object")

    def getObjectFactory():
        """Return the object factory used to create new objects for
        the field.
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
