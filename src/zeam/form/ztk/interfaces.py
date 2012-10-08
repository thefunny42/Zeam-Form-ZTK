# -*- coding: utf-8 -*-

from zope import interface
from zope.schema.interfaces import ISource
from zeam.form.base.interfaces import IField, IZeamFormBaseAPI


class IFormSourceBinder(ISource):
    """Marker interface used with zope.schema Choice in order to give
    a factory that takes the source.

    """

class ISchemaField(IField):
    """This is a field for zope schema field.
    """

    def fromUnicode(value):
        """This convert a value from a unicode string (or not).
        """


class IFieldCreatedEvent(interface.Interface):
    """A zeam.form Field have been created (out of a zope.schema
    Field).
    """
    field = interface.Attribute(
        u"Created field")
    interface = interface.Attribute(
        u"Interface on which the field have been crated")


class ICollectionField(IField):
    """This is a field for zope schema collection field. It is defined
    in order to be able to have a generic behavior on collections.
    """
    collectionType = interface.Attribute(
        u"Python type represented by this collection (like set, list...)")
    valueField = interface.Attribute(
        u"Field corresponding to the value type contained in the collection")
    allowAdding = interface.Attribute(
        u"Boolean flag to allow adding of values to the collection")
    allowRemove = interface.Attribute(
        u"Boolean flag to allow removing of values from the collection")
    inlineValidation = interface.Attribute(
        u"Boolean flag to validate data when a value is added or removed")


class IListField(ICollectionField):
    """This is a field for zope schema list field.
    """
    allowOrdering = interface.Attribute(
        u"Boolean flag to allow ordering of values")


class IObjectField(IField):
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
    customize = interface.Attribute(
        u"Decorator used to customize created fields")

    AddAction = interface.Attribute(
        u"Action to add a new content to one other")
    EditAction = interface.Attribute(
        u"Action to edit the values of a content")
    CancelAction = interface.Attribute(
        u"Action to cancel the submission of the form")
