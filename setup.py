#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'salesforce_bulkipy',
]

requires = [
    'httplib2>=0.7.5',
    'requests>=2.2.1',
    'unicodecsv>=0.13.0',
    'simple-salesforce>=0.72.2',
]

with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='salesforce-bulkipy',
    version='1.0',
    description='A Python library for the Salesforce Bulk API',
    long_description=readme,
    author='Shreyans Sheth',
    author_email='dev.shreyans96@gmail.com',
    url='https://github.com/wingify/salesforce-bulkipy',
    packages=packages,
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    license=license,
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
