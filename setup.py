#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup
import os

CONTAINING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

setup(
    name='qidata',
    version=open(os.path.join(CONTAINING_DIRECTORY,"qidata/VERSION")).read().split()[0],
    author='Louis-Kenzo Cahier',
    author_email='lkcahier@aldebaran.com',
    packages=['qidata', 'qidata.commands', 'qidata.gui', 'qidata.qiq'],
    package_data={"qidata":["VERSION"]},
    scripts=['bin/qidata'],
    url='.',
    license='LICENSE.txt',
    description='Dataset management CLI',
    long_description=open(os.path.join(CONTAINING_DIRECTORY,'README.md')).read(),
    install_requires=[
        "PySide >= 1.2.2",
        "python-xmp-toolkit >= 2.3.1"
        "argcomplete >= 1.1.0"
    ]
)

