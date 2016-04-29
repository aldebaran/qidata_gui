# -*- coding: utf-8 -*-

# Standard Library
import os.path
import re
# qidata
from .controllers import *


# ────────
# Datasets

# METADATA_FILENAME = "metadata.yaml" # Place-holder

# def isDataset(path):
#     return os.path.isdir(path) and os.path.isfile(os.path.join(path, METADATA_FILENAME))

# def isMetadataFile(path):
#     return  os.path.isfile(path) and os.path.basename(path) == METADATA_FILENAME

# ────────────────
# Data Controllers

LOOKUP_CONTROLLER_MODEL = {
    re.compile(".*\.png"): image_controller.ImageController,
    re.compile(".*\.jpg"): image_controller.ImageController
}

def isSupported(dataPath):
    for pattern in LOOKUP_CONTROLLER_MODEL:
        if pattern.match(dataPath):
            return True
    return False

def makeDataController(path):
    for pattern in LOOKUP_CONTROLLER_MODEL:
        if pattern.match(path):
            return LOOKUP_CONTROLLER_MODEL[pattern](path)
    raise TypeError("Controller not supported")
