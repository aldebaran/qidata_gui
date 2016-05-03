# -*- coding: utf-8 -*-

# Qt
from PySide.QtGui import QPixmap
# qidata
from ..dataitem import DataItem

class Image(DataItem):

    # ───────────
    # Constructor

    def __init__(self, source_path):
        # Load XMP and open it
        super(Image, self).__init__(source_path, True)

        # Load image
        self.data = QPixmap()
        self.data.load(source_path)

        self.annotations = dict()
