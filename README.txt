=============
zeam.form.ztk
=============

``zeam.form.ztk`` help you to integrate ``zeam.form.base`` with the
Zope Tool Kit. It provides:

- Form fields generation out of zope.schema fields, and zope.schema
  fields listed in a Zope interface,

- Default action to Add, Edit a content, Cancel a current action by
  returning on the default view of a content.

.. contents::

Example
=======

Let's create a form to edit a content. Here we have an interface for
our content::

  from zope import schema, interface

  class IClan(interface.Interface):
     pass

  class IPerson(interface.Interface):

     first_name = schema.TextLine(title=u"First Name")
     last_name = schema.TextLine(title=u"Last Name")
     age = schema.Int(title=u"Age", required=False)
     single = schema.Bool(title=u"Is single ?", default=True)

We assume that a Person is in a Clan. We can implement a Person::

  from persistence import Persistent

  class Person(Persistent):
      interface.implements(IPerson)

      first_name = None
      last_name = None
      age = None
      single = True

Add form
--------

You can add a new Person in a clan like this::

  import zeam.form.ztk as zeamform

  class Add(zeamform.Form):

      zeamform.context(IClan)

      label = u"New person"
      fields = zeamform.Fields(IPerson)
      actions =  zeamform.Actions(
           zeamform.AddAction("Add", factory=Person),
           zeamform.CancelAction("Cancel"))
      actions['add'].fieldName = 'last_name'


Edit form
---------

You can edit a Person like this::

  class Edit(zeamform.Form):

      zeamform.context(IPerson)
 
      label = u"Change person details"
      fields = zeamform.Fields(IPerson)
      actions =  zeamform.Actions(
           zeamform.EditAction("Update"),
           zeamform.CancelAction("Cancel"))

      ignoreContent = False


API
===

All the API of ``zeam.form.base`` is exported as well.

Actions
-------

``AddAction``
  Action which take an extra parameter, factory, to create an object
  stored on the content object. The created object is added with the
  help of ``INameChooser`` to get its identifier. The option
  ``fieldName`` will be used to lookup a value in the form data to
  give as potential identifier to ``INameChooser``. Afterwards the
  created object is edited (like EditAction does) with the form data.

``EditAction``
  Action which use the form data to change values on the content
  object, designated by the form fields, after validation of the form
  submission.

``CancelAction``
  Simple action which return on default view of the content without
  validating the form submission.


