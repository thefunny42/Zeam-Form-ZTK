import doctest
import unittest
from zeam.form.ztk.testing import FunctionalLayer


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs= {}

    suite = unittest.TestSuite()
    for filename in ['bool.txt', 'choice.txt', 'collection_set.txt',
                     'collection_list.txt', 'collection_object.txt',
                     'multichoice.txt', 'object.txt', 'date.txt',
                     'radio.txt', 'uri.txt', 'text.txt', 'time.txt',
                     'currency.txt', 'number.txt']:
        test = doctest.DocFileSuite(
            filename,
            optionflags=optionflags,
            globs=globs)
        test.layer = FunctionalLayer
        suite.addTest(test)

    return suite
