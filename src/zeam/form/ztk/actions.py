
from zope.app.container.interfaces import INameChooser
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.event import notify

from zeam.form.base import Action


class CancelAction(Action):
    """Cancel the current form and return on the default content view.
    """

    def __call__(self, form):
        form.redirect(form.url())


class EditAction(Action):
    """Edit the form content using the form fields.
    """

    def applyData(self, form, content, data):
        for field in form.fields:
            value = data.get(field.identifier, None)
            if value is not None:
                field.setContentValue(content, value)

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return

        content = form.getContent()
        self.applyData(form, content, data)
        notify(ObjectModifiedEvent(content))
        form.status = u"Modification saved"


class AddAction(EditAction):
    """Add a new content in the form content, saving the form fields
    on the newly created content.
    """

    fieldName = 'title'

    def __init__(self, title, factory):
        super(AddAction, self).__init__(title)
        self.factory = factory

    def create(self, form, data):
        content = self.factory()
        self.applyData(form, content, data)
        notify(ObjectCreatedEvent(content))
        return content

    def add(self, form, content, data):
        container = form.getContent()
        chooser = INameChooser(container)
        name = chooser.chooseName(data[self.fieldName], content)
        container[name] = content

    def nextURL(self, form, content):
        return form.url(content)

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return

        content = self.create(form, data)
        self.add(form, content, data)
        form.redirect(self.nextURL(form, content))

