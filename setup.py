#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def here(*a):
    return os.path.join(os.path.dirname(__file__), *a)


readme = open(here('README.md')).read()
requirements = [x.strip() for x in open(here('requirements.txt')).readlines()]

setup(
    name='inotifyexec',
    version='0.0.1',
    description='Uses inotify to watch a directory and execute a command on file change.',
    long_description=readme,
    author='Werner Beroux, Bennett Kanuka',
    author_email='werner@beroux.com, bkanuka@gmail.com',
    url='https://github.com/bkanuka/inotifyexec',
    packages=[
        'inotifyexec',
    ],
    package_dir={'inotifyexec': 'inotifyexec'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    keywords=['inotifyexec', 'inotify'],
    entry_points={
        'console_scripts': [
            'inotifyexec = inotifyexec.inotifyexec:main'
        ]
    },
)
