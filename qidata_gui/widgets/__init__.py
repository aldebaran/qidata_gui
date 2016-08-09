# -*- coding: utf-8 -*-

# Standard Library
import os.path
import re

import data_widgets
from main_widget import MainWidget


# ────────────
# Data Widgets

LOOKUP_WIDGET_MODEL = {
    "image": data_widgets.ImageWidget,
}

def makeWidget(widget_type, main_data=None):
    """
    Create relevant widget for required data type.
    @widget_type  :  Name of the data type to display with the widget (str)
    @main_data    :  Data to display
    @return       :  Widget containing the given data (MainWidget)
    @raise        :  TypeError if given type name is unknown
    """
    for qidata_file_type in LOOKUP_WIDGET_MODEL:
        if widget_type == qidata_file_type:
            return MainWidget(LOOKUP_WIDGET_MODEL[qidata_file_type](main_data))
    raise TypeError("No available widget for %s, available types are %s"
                        %(widget_type, LOOKUP_WIDGET_MODEL.keys())
                    )

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
