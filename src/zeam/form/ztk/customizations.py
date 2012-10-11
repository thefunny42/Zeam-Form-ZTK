
import sys
import martian
from martian.util import frame_is_module
from martian.error import GrokImportError

from zope.event import subscribers
from zope.interface.adapter import AdapterRegistry
from zope.interface import providedBy, implementedBy, Interface

from zeam.form.ztk.interfaces import IFieldCreatedEvent


class CustomizationRegistry(object):
    """Register and execute customization handlers.
    """

    def __init__(self):
        self._scheduled = False
        self._events = []
        self._origin = AdapterRegistry()
        self._field = AdapterRegistry()
        subscribers.append(self.watch)

    def watch(self, *events):
        if len(events) > 0 and IFieldCreatedEvent.providedBy(events[0]):
            self._events.append(events[0])

    def register(self, handler, options):
        if 'origin' in options:
            self._origin.register(
                (options['origin'], options.get('schema')),
                Interface,
                options.get('name', u''),
                handler)
        elif 'field' in options:
            self._field.register(
                (options['field'], options.get('schema')),
                Interface,
                options.get('name', u''),
                handler)
        elif 'schema' in options:
            self._origin.register(
                (Interface, options['schema']),
                Interface,
                options.get('name', u''),
                handler)
        else:
            raise AssertionError('Invalid customization')

    def execute(self, clear=True):
        for event in self._events:
            handler = None
            if event.origin is not None:
                # 1. Lookup customization with the original field
                required = (providedBy(event.origin), event.interface)
                # 1.a Original field and name
                handler = self._origin.lookup(
                    required, Interface, event.field.identifier)
                if handler is None:
                    # 1.b Original field without name
                    handler = self._origin.lookup(required, Interface)
                if handler is not None:
                    handler(event.field)
            if handler is None:
                # 2. No customization found, lookup with the zeam.form field
                required = (providedBy(event.field), event.interface)
                # 2.a zeam.form field and name
                handler = self._field.lookup(
                    required, Interface, event.field.identifier)
                if handler is None:
                    # 2.b zeam.form field without name
                    handler = self._field.lookup(required, Interface)
                if handler is not None:
                    handler(event.field)
        if clear:
            del self._events[:]
        self._scheduled = False

    def schedule(self, config):
        if not self._scheduled:
            config.action(
                discriminator=('customize fields',),
                callable=self.execute,
                args=tuple(),
                order=sys.maxint-1)
            self._scheduled = True

registry = CustomizationRegistry()


class customize:

    def __init__(self, origin=None, schema=None, field=None, name=u''):
        self.options = {'origin': origin, 'schema': schema,
                        'field':field, 'name': name}

    def __call__(self, handler):
        frame = sys._getframe(1)
        if not frame_is_module(frame):
            raise GrokImportError(
                '@customize can only be used on module level')
        if not self.options:
            raise GrokImportError(
                '@customize options are missing')

        customizations = frame.f_locals.get(
            '__zeam_form_customizations__', None)
        if customizations is None:
            frame.f_locals['__zeam_form_customizations__'] = customizations = []
        customizations.append((handler, self.options))
        return handler


class CustomizationGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, *kw):
        customizations = module_info.getAnnotation(
            'zeam.form.customizations', [])
        if customizations:
            for customization in customizations:
                registry.register(customization[0], customization[1])
            registry.schedule(config)
            return True
        return False
