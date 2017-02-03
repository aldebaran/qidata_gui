# -*- coding: utf-8 -*-

# local
from ..annotation_controller import AnnotationController

class ImageController(AnnotationController):

    # ───────────────
    # Private methods

    def _makeLocation(self, coordinates):
        if coordinates is not None:
            x=coordinates[0]
            y=coordinates[1]
            return [[x-30,y-30],[x+30,y+30]]
        else:
            return None