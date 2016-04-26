# -*- coding: utf-8 -*-

from .xmp import XMPFile, XMPMetadata, ALDEBARAN_NS

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
        return self.xmp_file.metadata[ALDEBARAN_NS]

    @property
    def xmp(self):
        return self.xmp_file.metadata

    # ───────────────
    # Context Manager

    def __enter__(self):
        self.xmp_file.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.xmp_file.__exit__(type, value, traceback)
