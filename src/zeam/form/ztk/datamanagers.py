# -*- coding: utf-8 -*-

from zeam.form.base.datamanager import ObjectDataManager


def makeGenericAdaptiveDataManager(*fields):

    class GenericAdaptiveDataManager(ObjectDataManager):
        """A data manager that adapt its content to an interface
        before doing anything.
        """
        fields = {}
        adapters = {}

        def __init__(self, content):
            for field in fields:
                interface = field._field.interface
                self.fields[field.identifier] = interface
                if (not interface.providedBy(content) and
                    not interface in self.adapters):
                    self.adapters[interface] = interface(content)
            self.content = content

        def _getAdapter(self, identifier):
            if not identifier in self.fields:
                return self.content
            return self.adapters.get(self.fields.get(identifier))

        def get(self, identifier):
            content = self._getAdapter(identifier)
            if content is not None:
                return getattr(content, identifier)
            raise KeyError(identifier)

        def set(self, identifier, value):
            content = self._getAdapter(identifier)
            if content is None:
                raise KeyError(identifier)
            setattr(content, identifier, value)

    return GenericAdaptiveDataManager
