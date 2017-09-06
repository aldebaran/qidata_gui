#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

CONTAINING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

try:
    from utils import get_version_from_tag
    __version__ = get_version_from_tag()
    open(os.path.join(CONTAINING_DIRECTORY,"qidata_gui/VERSION"), "w").write(__version__)
except ImportError:
    __version__=open(os.path.join(CONTAINING_DIRECTORY,"qidata_gui/VERSION")).read().split()[0]

package_list = find_packages(where=os.path.join(CONTAINING_DIRECTORY))

setup(
    name='qidata_gui',
    version=__version__,
    description='Graphical interface for qidata suite',
    long_description=open(os.path.join(CONTAINING_DIRECTORY,'README.md')).read(),
    url='https://gitlab.aldebaran.lan/qidata/qidata_gui',
    author='Surya Ambrose <sambrose@aldebaran.com>, Louis-Kenzo Cahier <lkcahier@aldebaran.com>',
    author_email='sambrose@aldebaran.com',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='metadata annotation tagging',
    packages=package_list,
    install_requires=[
        "PySide >= 1.2.4",
        "qidata >= 1.0.0a8",
        "argcomplete >= 1.1.0",
        "opencv-python >= 3.3",
        "image.py >= 0.3.0"
    ],
    package_data={"qidata_gui":["VERSION", "_resources/*.png"]},
    entry_points={
        'qidata.commands': [
            'annotate = qidata_apps.annotator.app',
            'extract = qidata_apps.rosbag_extractor.app',
            'open = qidata_apps.viewer.app',
        ],
    },
)

