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

And we can render it:

  >>> print form()
  <html>
    <head>
    </head>
    <body>
      <form action="http://127.0.0.1" method="post"
            enctype="multipart/form-data">
        <h1>People form</h1>
        <p>Form to send people outerspace</p>
        <div class="fields">
            <label class="field-label" for="form-name">Person name</label><br />
            <input id="form-name" name="form.name" value="" />
            <label class="field-label" for="form-age">Person age</label><br />
            <span class="field-description">Age in years</span><br />
            <input id="form-age" name="form.age" value="" />
        </div>
        <div class="actions">
            <input type="submit" id="form-send" name="form.send"
                   value="Send" />
        </div>
      </form>
    </body>
  </html>

Let's try to take a browser and submit that form:

  >>> root = getRootFolder()
  >>> root['person'] = context

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/person/personform')

  >>> namefield = browser.getControl('Person name')
  >>> namefield
  <Control name='form.name' type='text'>
  >>> namefield.value = 'Arthur Sanderman'

  >>> agefield = browser.getControl('Person age')
  >>> agefield
  <Control name='form.age' type='text'>
  >>> agefield.value = '42'

  >>> action = browser.getControl('Send')
  >>> action
  <SubmitControl name='form.send' type='submit'>

  >>> action.click()
  >>> print browser.contents
  <html>
    <head>
    </head>
    <body>
      <form action="http://localhost/person/personform"
            method="post" enctype="multipart/form-data">
        <p class="status-message">We sent Arthur Sanderman, age 42</p>
        <h1>People form</h1>
        <p>Form to send people outerspace</p>
        <div class="fields">
            <label class="field-label" for="form-name">Person name</label><br />
            <input id="form-name" name="form.name" value="" />
            <label class="field-label" for="form-age">Person age</label><br />
            <span class="field-description">Age in years</span><br />
            <input id="form-age" name="form.age" value="" />
        </div>
        <div class="actions">
            <input type="submit" id="form-send" name="form.send"
                   value="Send" />
        </div>
      </form>
    </body>
  </html>

"""
