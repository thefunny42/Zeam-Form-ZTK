# -*- coding: utf-8 -*-

from zeam.form.ztk.fields import SchemaField
from zeam.form.ztk.fields import registerSchemaField
from zope.schema import interfaces as schema_interfaces


def register():
    registerSchemaField(FloatSchemaField, schema_interfaces.IFloat)
    registerSchemaField(IntSchemaField, schema_interfaces.IInt)


class IntSchemaField(SchemaField):
    """A integer field.
    """

class FloatSchemaField(SchemaField):
    """A float field.
    """
