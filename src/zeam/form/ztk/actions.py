
from zeam.form.base import Action


class CancelAction(Action):

    def __call__(self, form):
        form.redirect(form.url())

