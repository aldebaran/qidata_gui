# -*- coding: utf-8 -*-

# Standard Library
import re

# qidata
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
    return False

def makeAnnotationController(path, user_name):
    for pattern in _LOOKUP_CONTROLLER_MODEL:
        if pattern.match(path):
            return _LOOKUP_CONTROLLER_MODEL[pattern](path, user_name)
    raise TypeError("Controller not supported")
