# -*- coding: utf-8 -*-

from qidata.xmp import XMPFile, XMPMetadata, ALDEBARAN_NS

class DataItem(object):

    # ───────────
    # Constructor

    def __init__(self, file_path, rw = False):
        self.xmp_file = XMPFile(file_path, rw)
        self.data = None

    # ──────────
    # Properties

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data

    @property
    def annotations(self):
        return self._annotations

    @annotations.setter
    def annotations(self, new_annotations):
        self._annotations = new_annotations

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

    # ───────────
    # General API

    def open(self):
        self.xmp_file.__enter__()
        return self

    def close(self):
        self.xmp_file.__exit__(None, None, None)

    # ───────────────
    # Context Manager

    def __enter__(self):
        return self.open()

    def __exit__(self, type, value, traceback):
        self.xmp_file.__exit__(type, value, traceback)
