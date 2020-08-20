# -*- coding: utf-8 -*-
"""
We are going to use a simple form with an edit action to edit a comment.

Monkeypatch i18n

  >>> import zope.i18n
  >>> import zope.i18n.config
  >>> old_1, old_2 = zope.i18n.negotiate, zope.i18n.config.ALLOWED_LANGUAGES
  >>> zope.i18n.negotiate = lambda context: 'en'
  >>> zope.i18n.config.ALLOWED_LANGUAGES = ['en']

Let's grok our example:

  >>> from zeam.form.ztk.testing import grok
  >>> grok('zeam.form.ztk.ftests.forms.editform_fixture')

Let's add a comment and try to edit it with our form:

  >>> from zeam.form.ztk.ftests.forms.editform_fixture import Comment
  >>> root = getRootFolder()
  >>> root['comment'] = Comment('zeam.form', 'Is great')
  >>> root['comment'].title
  'zeam.form'
  >>> root['comment'].comment
  'Is great'
  >>> root['comment'].name
  ''

  >>> from zope.testbrowser.wsgi import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Now acccess the edit form:

  >>> browser.open('http://localhost/comment/edit')
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> 'Modify your comment' in browser.contents
  True

  >>> title_field = browser.getControl('Title')
  >>> title_field
  <Control name='form.field.title' type='text'>
  >>> title_field.value
  'zeam.form'

  >>> comment_field = browser.getControl('Comment')
  >>> comment_field
  <Control name='form.field.comment' type='textarea'>
  >>> comment_field.value
  'Is great'

  >>> name_field = browser.getControl('Name')
  >>> name_field
  <Control name='form.field.name' type='text'>
  >>> name_field.value
  ''

We can now edit the content, and so it get modified:

  >>> title_field.value = 'zeam.form.ztk'
  >>> comment_field.value = 'Is far cooler than not ztk'
  >>> name_field.value = 'Arthur de la contee d`or'
  >>> change_button = browser.getControl('Change')
  >>> change_button
  <SubmitControl name='form.action.change' type='submit'>

  >>> change_button.click()
  >>> 'Modification saved' in browser.contents
  True

Modifications are saved, we have the new value if we reload the page:

  >>> browser.open('http://localhost/comment/edit')

  >>> title_field = browser.getControl('Title')
  >>> title_field.value
  'zeam.form.ztk'
  >>> comment_field = browser.getControl('Comment')
  >>> comment_field.value
  'Is far cooler than not ztk'
  >>> name_field = browser.getControl('Name')
  >>> name_field.value
  'Arthur de la contee d`or'

We can remove name, it will work as it is not required:

  >>> name_field.value = ''
  >>> change_button = browser.getControl('Change')
  >>> change_button.click()
  >>> 'Modification saved' in browser.contents
  True


And name is gone:

  >>> browser.open('http://localhost/comment/edit')

  >>> title_field = browser.getControl('Title')
  >>> title_field.value
  'zeam.form.ztk'
  >>> comment_field = browser.getControl('Comment')
  >>> comment_field.value
  'Is far cooler than not ztk'
  >>> name_field = browser.getControl('Name')
  >>> name_field.value
  ''

However comment is required:

  >>> comment_field.value = ''
  >>> change_button = browser.getControl('Change')
  >>> change_button.click()
  >>> 'Modification saved' in browser.contents
  False
  >>> 'There were errors' in browser.contents
  True

So no changes happened:

  >>> browser.open('http://localhost/comment/edit')

  >>> title_field = browser.getControl('Title')
  >>> title_field.value
  'zeam.form.ztk'
  >>> comment_field = browser.getControl('Comment')
  >>> comment_field.value
  'Is far cooler than not ztk'
  >>> name_field = browser.getControl('Name')
  >>> name_field.value
  ''

"""
