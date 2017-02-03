# -*- coding: utf-8 -*-

# local
from ..annotation_controller import AnnotationController

class AudioController(AnnotationController):

    # ───────────────
    # Private methods

    def _makeLocation(self, coordinates):
        if coordinates is not None:
            # TODO: create a metadata object suited for audio
            return
        else:
            return None