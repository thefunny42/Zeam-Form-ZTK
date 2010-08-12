=============
zeam.form.ztk
=============

``zeam.form.ztk`` help you to integrate `zeam.form.base`_ with the
Zope Tool Kit. It provides:

- Form fields generation out of zope.schema fields, and zope.schema
  fields listed in a Zope interface,

- Widgets for those fields,

- Default action to Add, Edit a content, Cancel a current action by
  returning on the default view of a content.

Like `zeam.form.base`_ the focus is to have an API usable by the
developer, not a support of theorical use-cases that you don't need.

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

  import zeam.form.ztk as form

  class Add(form.Form):

      form.context(IClan)

      label = u"New person"
      fields = form.Fields(IPerson)
      actions =  form.Actions(
           form.AddAction("Add", factory=Person),
           form.CancelAction("Cancel"))
      actions['add'].fieldName = 'last_name'


Edit form
---------

You can edit a Person like this::

  class Edit(form.Form):

      form.context(IPerson)

      label = u"Change person details"
      fields = form.Fields(IPerson)
      actions =  form.Actions(
           form.EditAction("Update"),
           form.CancelAction("Cancel"))

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


Fields
------

Currently supported fields:

- Date, Datetime: generate a text line input and parse/display the
  date using the locale,

- TextLine, Text, Boolean, URI, and numbers (Int, Float ...),

- Password,

- Choice: generate a select or a radio boxes (widget mode ``radio``),

- Object,

- Collections: List, Set, Tuple in input and display mode:

  - Collection of choices: generate a widget with a list of checkboxes,

  - Collection of objects: generate a table to edit multiple objects,

  - Other collection: generate a widget with generic add an remove actions.


For more documentation, please report to the doctests included in the code.


.. _zeam.form.base: http://pypi.python.org/pypi/zeam.form.base
