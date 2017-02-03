# -*- coding: utf-8 -*-

# Standard Library
import re

# qidata
from qidata import qidataset

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
    for pattern in _LOOKUP_CONTROLLER_MODEL:
        if pattern.match(path):
            return _LOOKUP_CONTROLLER_MODEL[pattern](path, user_name)
    if qidataset.isDataset(path):
        return dataset_controller.DataSetController(path, user_name)
    raise TypeError("No controller exists for this type of file")
