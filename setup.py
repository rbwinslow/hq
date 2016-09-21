#
# from distutils.core import setup
#
# setup(name='hq',
#       version='0.1',
#       description='Beautiful HTML querying, filtering, slicing and dicing!',
#       author_email='richard.b.winslow@gmail.com',
#       py_modules=['hq'])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

version = re.search("^__version__\s*=\s*'(.*)'", open('hq/hq.py').read(), re.M).group(1)


with open('README.rst', 'rb') as f:
    long_description = f.read().decode('utf-8')

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Topic :: Text Processing :: Markup :: HTML',
]

setup(name='hq',
      packages=find_packages(exclude=['test']),
      entry_points={'console_scripts': ['hq = hq.hq:main']},
      version=version,
      description='Command-line tool for querying, slicing & dicing HTML using the XPath/XQuery derivative HQuery.',
      long_description=long_description,
      author='Richard B. Winslow',
      author_email='richard.b.winslow@gmail.com',
      license='MIT',
      url='https://github.com/rbwinslow/hq',
      keywords='html xpath query xquery hquery jq cmdline cli',
      classifiers=classifiers,
      install_requires=['beautifulsoup4', 'docopt'])
