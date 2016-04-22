# -*- coding: utf-8 -*-

class Face:
    """Contains annotation details for a face"""
    def __init__(self, arg):
        self.name = ""

    # ──────────
    # Properties

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name