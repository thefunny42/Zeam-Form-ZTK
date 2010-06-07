#!/usr/bin/python
# -*- coding: utf-8 -*-

class InvariantsValidation(object):

    def __init__(self, *fields):
        self.interfaces = []
        for field in fields:
            interface = field._field.interface
            if interface not in self.interfaces:
                self.interfaces.append(interface)

    def validate(self, data):
        errors = []
        for interface in self.interfaces:
            interface.validateInvariants(date, errors)
        return errors
