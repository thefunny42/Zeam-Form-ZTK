import unittest
import doctest
from zeam.form.ztk.testing import FunctionalLayer


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs= {}

    suite = unittest.TestSuite()
    for filename in ['fields.txt', 'validation.txt']:
        dottedname = f'zeam.form.ztk.tests.{filename[:-4]}'
        test = doctest.DocFileSuite(
            dottedname,
            optionflags=optionflags,
            globs=globs)
        test.layer = FunctionalLayer
        suite.addTest(test)

    return suite
