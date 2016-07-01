# -*- coding: utf-8 -*-

# Standard Library
import os.path
import re

from image_widget import ImageWidget
from qidatawidget import QiDataWidget
from qidata_file import *


# ────────────
# Data Widgets

LOOKUP_WIDGET_MODEL = {
    "image": ImageWidget,
}

def makeWidget(widget_type, main_data=None):
    """
    Create relevant widget for required data type.
    @widget_type  :  Name of the data type to display with the widget (str)
    @main_data    :  Data to display
    @return       :  Widget containing the given data (QiDataWidget)
    @raise        :  TypeError if given type name is unknown
    """
    for qidata_file_type in LOOKUP_WIDGET_MODEL:
        if widget_type == qidata_file_type:
            return QiDataWidget(LOOKUP_WIDGET_MODEL[qidata_file_type](main_data))
    raise TypeError("No available widget for %s, available types are %s"
                        %(qidata_file_type, LOOKUP_WIDGET_MODEL.keys())
                    )

# ––––––––––––––––––––––––––––
# Convenience version variable

VERSION = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "VERSION")).read().split()[0]

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
