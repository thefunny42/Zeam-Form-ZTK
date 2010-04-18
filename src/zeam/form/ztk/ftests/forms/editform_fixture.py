
from zeam.form import ztk
from zope import interface, schema

from grokcore import component as grok


class IComment(interface.Interface):
    title = schema.TextLine(
        title=u"Title",
        required=True)
    comment = schema.Text(
        title=u"Comment",
        required=True)
    name = schema.TextLine(
        title=u"Name",
        required=False)


class Comment(grok.Context):
    grok.implements(IComment)

    def __init__(self, title, comment, name=''):
        self.title = title
        self.comment = comment
        self.name = name


class Edit(ztk.Form):
    label = u"Modify your comment"

    ignoreContent = False
    fields = ztk.Fields(IComment)
    actions = ztk.Actions(ztk.EditAction(u"Change"))


from zope.app.security.protectclass import protectName, protectSetAttribute
# Need to declare security for Zope madness

protectName(Comment, 'title', 'zope.Public')
protectName(Comment, 'comment', 'zope.Public')
protectName(Comment, 'name', 'zope.Public')

# Everybody as edit right, so test are simpler
protectSetAttribute(Comment, 'title', 'zope.Public')
protectSetAttribute(Comment, 'comment', 'zope.Public')
protectSetAttribute(Comment, 'name', 'zope.Public')
