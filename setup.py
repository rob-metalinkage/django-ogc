#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = '0.1'

import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='ogcext',
    version = VERSION,
    description='OGC custom utilities',
    packages=['ogcext'],
    include_package_data=True,
    author='Rob Atkinson',
    author_email='rob@metalinkage.com,au',
    license='CC',
    long_description=read('README.md'),
    zip_safe=False,
    install_requires = ['django-skosxl',
                        'django-rdf_io',
                        'lxml', 'smuggler'   
                        ]

)

