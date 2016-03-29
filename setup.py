#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import platform

if sys.version_info < (2, 5):
    raise Exception('Flakeplus requires Python 2.5 or higher.')

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    raise
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages           # noqa
    from setuptools.command.test import test              # noqa

NAME = 'flakeplus'
entrypoints = {}
extra = {}

# -*- Classifiers -*-

classes = """
    Development Status :: 5 - Production/Stable
    License :: OSI Approved :: BSD License
    Intended Audience :: Developers
    Environment :: Console
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.5
    Programming Language :: Python :: 2.6
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Programming Language :: Python :: Implementation :: Jython
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

# -*- Distribution Meta -*-

import re
re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
re_vers = re.compile(r'VERSION\s*=\s*\((.*?)\)')
re_doc = re.compile(r'^"""(.+?)"""')
rq = lambda s: s.strip("\"'")

def add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, rq(attr_value)), )


def add_version(m):
    v = list(map(rq, m.groups()[0].split(', ')))
    return (('VERSION', '.'.join(v[0:3]) + ''.join(v[3:])), )


def add_doc(m):
    return (('doc', m.groups()[0]), )

pats = {re_meta: add_default,
        re_vers: add_version,
        re_doc: add_doc}
here = os.path.abspath(os.path.dirname(__file__))
meta_fh = open(os.path.join(here, 'flakeplus/__init__.py'))
try:
    meta = {}
    for line in meta_fh:
        if line.strip() == '# -eof meta-':
            break
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()

# -*- Installation Dependencies -*-

install_requires = ['unipath']

# -*- Tests Requires -*-

tests_require = ['nose', 'mock']
if sys.version_info < (2, 7):
    tests_require.append('unittest2')

# -*- Long Description -*-

if os.path.exists('README.rst'):
    long_description = codecs.open('README.rst', 'r', 'utf-8').read()
else:
    long_description = 'See http://pypi.python.org/pypi/flakeplus'

# -*- Entry Points -*- #

entrypoints['console_scripts'] = [
        'flakeplus = flakeplus:main',
]

# -*- %%% -*-

setup(
    name=NAME,
    version=meta['VERSION'],
    description=meta['doc'],
    author=meta['author'],
    author_email=meta['contact'],
    url=meta['homepage'],
    platforms=['any'],
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    classifiers=classifiers,
    entry_points=entrypoints,
    long_description=long_description,
    **extra)
