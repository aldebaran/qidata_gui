# -*- coding: utf-8 -*-

# Standard Library
import os.path
# qidata
from qidata.models import *


# ────────
# Datasets

METADATA_FILENAME = "dataset.yaml"

def isDataset(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, METADATA_FILENAME))

def isMetadataFile(path):
    return  os.path.isfile(path) and os.path.basename(path) == METADATA_FILENAME

# ──────────
# Data Items

LOOKUP_ITEM_MODEL = {
    "png": image.Image,
    "jpg": image.Image
}

def isSupportedItem(path):
    return True
    # TODO
