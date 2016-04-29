# -*- coding: utf-8 -*-

from PySide.QtCore import QObject, Signal

class DataController(QObject):

    # ──────
    # Signal

    selectionChanged = Signal()

    # ───────────
    # Constructor

    def __init__(self):
        super(DataController, self).__init__()
        pass

    # ──────────
    # Properties

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, new_widget):
        self._widget = new_widget

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, new_model):
        self._model = new_model

    @property
    def modelHandler(self):
        return self._modelHandler

    @modelHandler.setter
    def modelHandler(self, new_modelHandler):
        self._modelHandler = new_modelHandler