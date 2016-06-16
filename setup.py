#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup
import os

CONTAINING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

setup(
    name='annotator',
    version=open(os.path.join(CONTAINING_DIRECTORY,"annotator/VERSION")).read().split()[0],
    author='Surya Ambrose',
    author_email='sambrose@aldebaran.com',
    packages=['annotator', 'annotator.commands', 'annotator.gui', 'annotator.qiq'],
    package_data={"annotator":["VERSION"]},
    scripts=['bin/annotator'],
    url='.',
    license='LICENSE.txt',
    description='Graphical dataset annotator',
    long_description=open(os.path.join(CONTAINING_DIRECTORY,'README.md')).read(),
    test_suite="tests",
    install_requires=[
        "PySide >= 1.2.2",
        "qidata_widgets >= 0.1.1",
        "qidata_file >= 0.1",
        "argcomplete >= 1.1.0"
    ]
)

