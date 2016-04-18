#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from .xmp import XMPFile, XMPMetadata, ALDEBARAN_NS_1

class Metadata(object):
    def __init__(self, xmp_metadata):
        self.xmp_metadata = xmp_metadata

    @property
    def aldebaran(self):
        try:
            return self.xmp_metadata[ALDEBARAN_NS_1]
        except KeyError:
            raise AttributeError("No Aldebaran-namespace metadata")

class DataItem(object):
    def __init__(self, file_path, rw = False):
        self.xmp_file = XMPFile(file_path, rw)

    # ──────────
    # Properties

    @property
    def rw(self):
        return self.xmp_file.rw

    @property
    def file_path(self):
        return self.xmp_file.file_path

    @property
    def metadata(self):
        return Metadata(self.xmp_file.metadata)

    # ───────────────
    # Context Manager

    def __enter__(self):
        self.xmp_file.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.xmp_file.__exit__(type, value, traceback)
