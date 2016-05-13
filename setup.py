#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup
import os

CONTAINING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

setup(
    name='qidata_widgets',
    version=open(os.path.join(CONTAINING_DIRECTORY,"qidata_widgets/VERSION")).read().split()[0],
    author='Surya Ambrose',
    author_email='sambrose@aldebaran.com',
    packages=['qidata_widgets'],
    package_data={"qidata_widgets":["VERSION"]},
    url='.',
    license='LICENSE.txt',
    description='Contains different Qt Widget to display data_objects and interact with it.',
    long_description=open(os.path.join(CONTAINING_DIRECTORY,'README.md')).read(),
    install_requires=[
        "qidata_objects >= 0.1"
    ]
)

