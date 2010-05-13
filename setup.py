from setuptools import setup, find_packages
import os

version = '1.0b2'

tests_require = [
    'zope.app.authentication',
    'zope.app.security',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    'zope.configuration',
    'zope.publisher',
    'zope.securitypolicy',
    'zope.testbrowser',
    'zope.testing',
    ]

setup(name='zeam.form.ztk',
      version=version,
      description="Zope Toolkit support for zeam.form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Programming Language :: Zope",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zeam form zope schema edit content',
      author='Sylvain Viollon',
      author_email='thefunny@gmail.com',
      url='http://pypi.python.org/pypi/zeam.form.ztk',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'grokcore.component',
        'megrok.chameleon',
        'setuptools',
        'zeam.form.base',
        'zope.app.container',
        'zope.component',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
