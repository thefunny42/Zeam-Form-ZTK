
from zeam.form import base
from zope import interface, schema

from grokcore import component as grok


class IPerson(interface.Interface):
    name = schema.TextLine(
        title=u"Person name")
    age = schema.Int(
        title=u"Person age",
        description=u"Age in years")


class Person(grok.Context):
    grok.implements(IPerson)


class PersonForm(base.Form):

    label = u"People form"
    description = u"Form to send people outerspace"

    fields = base.Fields(IPerson)

    @base.action(u"Send")
    def send(self):
        data, errors = self.extractData()
        self.status = u"We sent %s, age %d" % (data['name'], data['age'])

