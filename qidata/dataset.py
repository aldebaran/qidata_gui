#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os.path

METADATA_FILENAME = "dataset.yaml"

class Metadata:
    def __init__(path):
        pass

def isDataset(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, METADATA_FILENAME))

def isMetadataFile(path):
    return  os.path.isfile(path) and os.path.basename(path) == METADATA_FILENAME

class Dataset:
    pass
