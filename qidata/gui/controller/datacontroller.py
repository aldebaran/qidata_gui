# -*- coding: utf-8 -*-

from PySide.QtCore import QObject, Signal
from PySide.QtGui import QMessageBox

class SelectionChangeCanceledByUser(Exception):
    def __init__(self):
        pass

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

    def onExit(self, auto_save):
        savingRequest = (QMessageBox.Yes if auto_save else self.widget.askForDataSave())
        if savingRequest == QMessageBox.Yes:
            self.modelHandler.save_annotations()
        if savingRequest == QMessageBox.Cancel:
            raise SelectionChangeCanceledByUser()