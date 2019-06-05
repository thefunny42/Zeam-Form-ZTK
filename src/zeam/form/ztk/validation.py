# -*- coding: utf-8 -*-

from zope.interface.interfaces import IMethod
from zope.interface import directlyProvides, Invalid
from zeam.form.base.markers import NO_VALUE
from zeam.form.ztk.interfaces import ISchemaField


class Data(object):
    """Wraps the data dicts into an object, acting as
    an attribute access proxy.
    """
    def __init__(self, interface, data):
        self.interface = interface
        self.data = data
        directlyProvides(self, interface)

    def __getattr__(self, name):
        try:
            field = self.interface[name]
        except KeyError:
            raise AttributeError(name)

        if IMethod.providedBy(field):
            raise RuntimeError("Data value is not a schema field", name)

        value = self.data.getWithDefault(name)

        if value is NO_VALUE:
            raise AttributeError(name)

        return value


class InvariantsValidation(object):
    """Validates the invariants of the given fields' interfaces.
    """
    def __init__(self, form, fields):
        self.form = form
        self.interfaces = []
        for field in fields:
            if (field.interface is not None and
                field.interface not in self.interfaces):
                self.interfaces.append(field.interface)

    def validate(self, data):
        errors = []
        for interface in self.interfaces:
            obj = Data(interface, data)
            try:
                interface.validateInvariants(obj, errors)
            except Invalid as error:
                pass
            for error in errors:
                yield error.args[0]
