# -*- coding: utf-8 -*-

# qidata
from qidata import makeMetadataObject

# local
from ..annotation_controller import AnnotationController

class ImageController(AnnotationController):

    # ───────────
    # Constructor

    def __init__(self, source_path, user_name):
        AnnotationController.__init__(self, source_path, user_name)

    # ───────────────
    # Private methods

    def _makeLocation(self, coordinates):
        if coordinates is not None:
            x=coordinates[0]
            y=coordinates[1]
            return [[x-30,y-30],[x+30,y+30]]
        else:
            return None