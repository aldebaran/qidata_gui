# -*- coding: utf-8 -*-

# qidata
from qidata import makeMetadataObject

# local
from ..annotation_controller import AnnotationController

class AudioController(AnnotationController):

    # ───────────
    # Constructor

    def __init__(self, source_path, user_name):
        super(AudioController, self).__init__(source_path, user_name)

    # ───────────────
    # Private methods

    def _makeLocation(self, coordinates):
        if coordinates is not None:
            # TODO: create a metadata object suited for audio
            return
        else:
            return None