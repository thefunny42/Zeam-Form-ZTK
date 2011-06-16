# -*- coding: utf-8 -*-
"""
We are going to use a simple form with an edit action to edit a comment.

Let's grok our example:

  >>> from zeam.form.ztk.testing import grok
  >>> grok('zeam.form.ztk.ftests.forms.editform_fixture')

Let's add a comment and try to edit it with our form:

  >>> from zeam.form.ztk.ftests.forms.editform_fixture import Comment
  >>> root = getRootFolder()
  >>> root['comment'] = Comment(u'zeam.form', u'Is great')
  >>> root['comment'].title
  u'zeam.form'
  >>> root['comment'].comment
  u'Is great'
  >>> root['comment'].name
  u''

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Now acccess the edit form:

  >>> browser.open('http://localhost/comment/edit')
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> u'Modify your comment' in browser.contents
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
