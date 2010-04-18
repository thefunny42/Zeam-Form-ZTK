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

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Now acccess the edit form:

  >>> browser.open('http://localhost/comment/edit')
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> u'Modify your comment' in browser.contents
  True

  >>> titlefield = browser.getControl('Title')
  >>> titlefield
  <Control name='form.field.title' type='text'>
  >>> titlefield.value
  'zeam.form'

  >>> commentfield = browser.getControl('Comment')
  >>> commentfield
  <Control name='form.field.comment' type='textarea'>
  >>> commentfield.value
  'Is great'

  >>> namefield = browser.getControl('Name')
  >>> namefield
  <Control name='form.field.name' type='text'>
  >>> namefield.value
  ''

We can now edit the content, and so it get modified:

  >>> titlefield.value = 'zeam.form.ztk'
  >>> commentfield.value = 'Is far cooler than not ztk'
  >>> changebutton = browser.getControl('Change')
  >>> changebutton
  <SubmitControl name='form.action.change' type='submit'>

  >>> changebutton.click()
  >>> 'Modification saved' in browser.contents
  True


"""
