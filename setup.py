#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

CONTAINING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

setup(
    name='qidata_gui',
    version=open(os.path.join(CONTAINING_DIRECTORY,"qidata_gui/VERSION")).read().split()[0],
    author='Surya Ambrose <sambrose@aldebaran.com>, Louis-Kenzo Cahier <lkcahier@aldebaran.com>',
    author_email='sambrose@aldebaran.com',
    packages=find_packages("."),
    package_data={"qidata_gui":["VERSION"]},
    url='.',
    license='LICENSE.txt',
    description='Contains Qt Widgets to display metadata objects and interact with it, and also provide Qt Apps',
    long_description=open(os.path.join(CONTAINING_DIRECTORY,'README.md')).read(),
    install_requires=[
        "PySide >= 1.2.2",
        "qidata >= 0.3.0",
        "argcomplete >= 1.1.0"
    ]
)

