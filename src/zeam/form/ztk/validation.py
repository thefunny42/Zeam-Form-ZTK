# -*- coding: utf-8 -*-

from zope.interface.interfaces import IMethod
from zope.interface import directlyProvides, Invalid

UNAVAILABLE = object()


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

        data = self.data
        value = data.get(name, UNAVAILABLE)

        if value is UNAVAILABLE:
            raise AttributeError(name)

        return value


class InvariantsValidation(object):
    """Validates the invariants of the given fields' interfaces.
    """
    def __init__(self, fields):
        self.interfaces = []
        for field in fields:
            interface = field._field.interface
            if interface not in self.interfaces:
                self.interfaces.append(interface)

    def validate(self, data):
        errors = []
        for interface in self.interfaces:
            obj = Data(interface, data)
            try:
                interface.validateInvariants(obj, errors)
            except Invalid:
                pass  # We continue to get a complete errors log.
        return errors
