#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Softbank Robotics Europe
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        "qidata >= 1.0.0",
        "argcomplete >= 1.1.0",
        "opencv-python >= 3.3",
        "image.py >= 0.4.1"
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

