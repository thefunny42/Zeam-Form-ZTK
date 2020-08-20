from setuptools import setup, find_packages
import os

version = '1.4.0'

tests_require = [
    'zope.app.schema',
    'zope.app.wsgi',
    'zope.security',
    'zope.testing',
    'zeam.form.base [test]'
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
      namespace_packages=['zeam', 'zeam.form'],
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'chameleon >= 3.8',
          'grokcore.component',
          'grokcore.view',
          'grokcore.security',
          'grokcore.chameleon >= 1.0.3',
          'setuptools',
          'zeam.form.base >= 1.4.0',
          'zope.component',
          'zope.container',
          'zope.event',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.publisher',
          'zope.schema >= 3.8',
          'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require,
                        'email': ['z3c.schema'],
                        'fanstatic': ['fanstatic',
                                      'js.jquery',
                                      'zeam.jsontemplate']},
      entry_points="""
      # -*- Entry points: -*-
      [zeam.form.components]
      default = zeam.form.ztk.fields:registerDefault
      bool = zeam.form.ztk.widgets.bool:register
      choice = zeam.form.ztk.widgets.choice:register
      collection = zeam.form.ztk.widgets.collection:register
      date = zeam.form.ztk.widgets.date:register
      email = zeam.form.ztk.widgets.email:register
      number = zeam.form.ztk.widgets.number:register
      object = zeam.form.ztk.widgets.object:register
      password = zeam.form.ztk.widgets.password:register
      text = zeam.form.ztk.widgets.text:register
      textline = zeam.form.ztk.widgets.textline:register
      time = zeam.form.ztk.widgets.time:register
      uri = zeam.form.ztk.widgets.uri:register
      [fanstatic.libraries]
      zeam.form.ztk.widgets = zeam.form.ztk.widgets.collection:library
      """,
      )
