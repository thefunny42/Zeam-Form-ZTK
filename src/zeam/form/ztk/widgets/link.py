
from zeam.form.base.interfaces import IField
from zeam.form.base.widgets import DisplayFieldWidget
from zeam.form.base.markers import ModeMarker

from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.traversing.browser.interfaces import IAbsoluteURL

from grokcore import component as grok


class LinkFieldWidget(DisplayFieldWidget):
    grok.adapts(IField, Interface, Interface)
    grok.name('link')

    def url(self):
        context = self.form.context
        return getMultiAdapter((context, self.request), IAbsoluteURL)()


LINK = ModeMarker('LINK', extractable=False)

