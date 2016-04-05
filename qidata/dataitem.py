#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from libxmp import XMPFiles

class DataItem:
    def __init__(self):
        self.xmp = None

    def loadXMP(self, path):
        self.xmp = XMPFiles(path).get_xmp()

    def saveXMP(self, path):
        if xmp is None: return
        # TODO
