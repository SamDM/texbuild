#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'texbuild'
DESCRIPTION = 'Easy clean latex compiler using latexmk under the hood'
URL = 'https://gitlab.psb.ugent.be/blah-blah'
EMAIL = 'sam.demeyer@psb.ugent.be'
AUTHOR = 'Sam De Meyer <samey>'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = '0.1.0'

# What packages are required for this module to be executed?
REQUIRED = []

# What packages are optional?
EXTRAS = {
    # 'fancy-feature': ['some-lib']
}

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    here = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["test"]),
    entry_points={
        'console_scripts': ['texbuild=texbuild.build:main'],
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
