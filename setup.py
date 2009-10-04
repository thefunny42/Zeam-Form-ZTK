from setuptools import setup, find_packages
import os

version = '1.0'

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
      url='',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'zope.interface',
        'zope.component',
        'grokcore.component',
        'zope.schema',
        'zeam.form.base',
        # Test
        'zope.securitypolicy',
        'zope.app.authentication',
        'zope.app.testing',
        'zope.app.zcmlfiles',
        'zope.testing',
        'zope.testbrowser',
        ],
      )
