# -*- coding: utf-8 -*-

import zeam.form.ztk
from grokcore.component import zcml
from zope.app.wsgi.testlayer import BrowserLayer
from zope.configuration.config import ConfigurationMachine
from zope.testbrowser.wsgi import TestBrowserLayer


class Layer(TestBrowserLayer, BrowserLayer):
    pass



FunctionalLayer = Layer(zeam.form.ztk, allowTearDown=True)


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok(module_name, config)
    config.execute_actions()
