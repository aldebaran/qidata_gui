# -*- coding: utf-8 -*-

"""
qidata_gui package
==================

This package contains all widgets necessary to display data and any metadata linked to it.
It also contains several graphical applications using those widgets.
"""

# Standard libraries
import os as _os

# ––––––––––––––––––––––––––––
# Convenience version variable

VERSION = open(_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),
                             "VERSION")
              ).read().split()[0]

RESOURCES_DIR = _os.path.join(_os.path.dirname(_os.path.realpath(__file__)),
                              "_resources")

from qidataframe_widget import QiDataFrameWidget
from qidatasensor_widget import QiDataSensorWidget
from qidataset_widget import QiDataSetWidget

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
