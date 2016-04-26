# -*- coding: utf-8 -*-

# Standard Library
import os.path
import re
# qidata
from .widgets import *
from ..models.dataitems import *


# ────────────
# Data Widgets

LOOKUP_WIDGET_MODEL = {
    image.Image: image_widget.ImageWidget,
}

def makeWidget(dataItem):
    for dataItemType in LOOKUP_WIDGET_MODEL:
        if isinstance(dataItem, dataItemType):
            return LOOKUP_WIDGET_MODEL[dataItemType](dataItem)
    raise TypeError("No available widget for this item")
