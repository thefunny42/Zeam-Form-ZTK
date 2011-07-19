# -*- coding: utf-8 -*-

import zeam.form.ztk
from grokcore.component import zcml
from zope.app.wsgi.testlayer import BrowserLayer
from zope.configuration.config import ConfigurationMachine


FunctionalLayer = BrowserLayer(zeam.form.ztk)

def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok(module_name, config)
    config.execute_actions()
