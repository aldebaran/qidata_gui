# -*- coding: utf-8 -*-

# Qt
from PySide.QtGui import QPixmap
# qidata
from qidata.dataitem import DataItem

class Image(DataItem):
    def __init__(self, source_path):
        self.pixmap = QPixmap.load(source_path)
        self.loadXMP(source_path)

    @staticmethod
    def fromFile(source_path):
        # TODO
        pass

    @staticmethod
    def fromNaoqiImage(source_buffer):
        # TODO
        pass
