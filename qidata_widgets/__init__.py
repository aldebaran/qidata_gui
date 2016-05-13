# -*- coding: utf-8 -*-

# Standard Library
import os.path
import re

from image_widget import ImageWidget
from qidata_file import *


# ────────────
# Data Widgets

LOOKUP_WIDGET_MODEL = {
    Image: ImageWidget,
}

def makeWidget(qidataFile):
    for qidataFileType in LOOKUP_WIDGET_MODEL:
        if isinstance(qidataFile, qidataFileType):
            return LOOKUP_WIDGET_MODEL[qidataFileType](qidataFile)
    raise TypeError("No available widget for this item")

# ––––––––––––––––––––––––––––
# Convenience version variable

VERSION = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "VERSION")).read().split()[0]

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
