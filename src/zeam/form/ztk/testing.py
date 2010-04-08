
import os.path

import zeam.form.ztk

from zope.app.testing.functional import ZCMLLayer, FunctionalTestSetup
from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml

ftesting_zcml = os.path.join(
    os.path.dirname(zeam.form.ztk.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok(module_name, config)
    config.execute_actions()
