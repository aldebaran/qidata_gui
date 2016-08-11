# -*- coding: utf-8 -*-

# Standard Library
import os.path
# Qt
from PySide.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox
from PySide.QtCore import Signal
# qidata
from qidata.files import *
from qidata_gui.widgets import MainWidget
from qidata.types import MetadataType

class AnnotationSelectorWidget(QWidget):
    """
    Widget to select which annotations to view.
    """

    # ───────
    # Signals

    userChanged = Signal(str)

    # ───────────
    # Constructor

    def __init__(self, parent=None):
        super(AnnotationSelectorWidget, self).__init__(parent)

        ## VIEW DEFINITION

        self.user_selector_widget = QComboBox(self)
        self.user_selector_widget.setEnabled(True)
        self.user_selector_widget.currentIndexChanged['QString'].connect(self.userChanged.emit)

        # Main layout
        self.main_hlayout = QHBoxLayout(self)
        self.main_hlayout.addWidget(self.user_selector_widget)
        self.setLayout(self.main_hlayout)


class CentralWidget(QWidget):
    """Central viewer of the annotator."""

    # ───────
    # Signals

    objectAdditionRequired = Signal(list)
    objectTypeChangeRequested = Signal([MetadataType])
    userChanged = Signal(str)

    # ───────────
    # Constructor

    def __init__(self, main_widget, parent=None):
        """
        Constructor for CentralWidget. This will instanciate a QWidget
        containing all necessary interactive commands for annotation.

        @main_widget : qidata_widget object
        """
        super(CentralWidget, self).__init__(parent)

        ## VIEW DEFINITION

        # First widget layer: annotation selector
        self.annotation_selector_widget = AnnotationSelectorWidget(self)
        self.annotation_selector_widget.userChanged.connect(self.userChanged.emit)

        # Second widget layer: specialized qidata_widget
        # makeWidget("image", self.modelHandler)
        self.main_widget = MainWidget(main_widget)
        self.main_widget.objectAdditionRequired.connect(self.objectAdditionRequired.emit)
        self.main_widget.objectTypeChangeRequested.connect(self.objectTypeChangeRequested.emit)

        # Main layout
        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.addWidget(self.annotation_selector_widget)
        self.main_vlayout.addWidget(self.main_widget)
        self.setLayout(self.main_vlayout)

    # ───────
    # Methods

    def addObject(self, coordinates):
        return self.main_widget.addMetadataObjectToView(coordinates)

    def displayObject(self, qidata_object):
        self.main_widget.displayMetadataObjectDetails(qidata_object)

    def askForItemDeletion(self, item):
        response = QMessageBox.warning(self, "Suppression", "Are you sure you want to remove this annotation ?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            self.main_widget.removeMetadataObject(item)
            return True
        return False

    def askForDataSave(self):
        response = QMessageBox.warning(self, "Leaving..", "You are about to leave this file. Do you want to save your modifications ?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        return response