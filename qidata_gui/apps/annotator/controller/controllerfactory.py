# -*- coding: utf-8 -*-

# Standard Library
import os.path
import re
# qidata
from .controllers import *

# ────────────────
# Data Controllers

LOOKUP_CONTROLLER_MODEL = {
    re.compile(".*\.png"): image_controller.ImageController,
    re.compile(".*\.jpg"): image_controller.ImageController,
    re.compile(".*\.wav"): audio_controller.AudioController
}

def isSupported(dataPath):
    for pattern in LOOKUP_CONTROLLER_MODEL:
        if pattern.match(dataPath):
            return True
    return False

def makeDataController(path, user_name):
    for pattern in LOOKUP_CONTROLLER_MODEL:
        if pattern.match(path):
            return LOOKUP_CONTROLLER_MODEL[pattern](path, user_name)
    raise TypeError("Controller not supported")
