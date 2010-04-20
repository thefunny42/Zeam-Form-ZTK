# -*- coding: utf-8 -*-

from zeam.form.ztk.fields import SchemaField
from zeam.form.ztk.fields import registerSchemaField
from zope.schema import interfaces as schema_interfaces


class FloatSchemaField(SchemaField):
    """A datetime field.
    """

registerSchemaField(FloatSchemaField, schema_interfaces.IFloat)
