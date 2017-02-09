# -*- coding: utf-8 -*-

# Standard Library
import re

# qidata
from qidata import qidataset

from qidata_gui.widgets import QiDataWidget, QiDataSetWidget

# local
from .controllers import *

# ────────────────
# Data Controllers

_LOOKUP_CONTROLLER_MODEL = {
    re.compile(".*\.png"): image_controller.ImageController,
    re.compile(".*\.jpg"): image_controller.ImageController,
    re.compile(".*\.wav"): audio_controller.AudioController
}

def isSupported(dataPath):
    for pattern in _LOOKUP_CONTROLLER_MODEL:
        if pattern.match(dataPath):
            return True
    return qidataset.isDataset(dataPath)

def makeAnnotationController(path, user_name):
    if qidataset.isDataset(path):
        return QiDataSetWidget(path, user_name)
    return QiDataWidget(path, user_name)
