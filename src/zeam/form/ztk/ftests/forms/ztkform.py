"""
We are going to define a simple form with an action and two fields
coming from a Zope interface.

We put our example in a separate file, since the configure.zcml of
zeam.form needs to be loaded in order to be able to create the fields,
which is no the case when the tests are collected.

Let's grok our example:

  >>> from zeam.form.ztk.testing import grok
  >>> grok('zeam.form.ztk.ftests.forms.ztkform_fixture')

We can now lookup our form by the name of its class:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zeam.form.ztk.ftests.forms.ztkform_fixture import Person
  >>> context = Person()

  >>> from zope import component
  >>> form = component.getMultiAdapter(
  ...     (context, request), name='personform')
  >>> form
  <zeam.form.ztk.ftests.forms.ztkform_fixture.PersonForm object at ...>

  >>> len(form.actions)
  1
  >>> len(form.fields)
  2


Integration test
----------------

Let's try to take a browser and submit that form:

  >>> root = getRootFolder()
  >>> root['person'] = context

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

We can access the form, fill it and submit it:

  >>> browser.open('http://localhost/person/personform')
  >>> namefield = browser.getControl('Person name')
  >>> namefield
  <Control name='form.field.name' type='text'>
  >>> namefield.value = 'Arthur Sanderman'

  >>> agefield = browser.getControl('Person age')
  >>> agefield
  <Control name='form.field.age' type='text'>
  >>> agefield.value = '42'

  >>> action = browser.getControl('Send')
  >>> action
  <SubmitControl name='form.action.send' type='submit'>

  >>> action.click()
  >>> 'We sent Arthur Sanderman, age 42' in browser.contents
  True

"""
