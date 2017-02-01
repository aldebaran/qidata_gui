# -*- coding: utf-8 -*-

# Standard Library
import os.path

# Qt
from PySide.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
from PySide.QtCore import Signal

# qidata
from qidata.files import *
from qidata import MetadataType

# qidata_gui
from qidata_gui.widgets import QiDataWidget

class AnnotationInterface(QWidget):
    """
    Graphical interface allowing to modify the annotation of a file. It consists
    of two elements:
        - A ``QtGui.QComboBox`` to select which annotator's work we wish to see
        - A ``qidata_gui.widget.qidata_widget.QiDataWidget`` to display the QiDataObject
        to see and/or modify
    """

    # ───────
    # Signals

    newMetadataAdditionRequested = Signal(list)
    metadataTypeChangeRequested = Signal([MetadataType])
    userChanged = Signal(str)

    # ───────────
    # Constructor

    def __init__(self, qidata_object, parent=None):
        """
        Constructor for AnnotationInterface. This will instanciate a QWidget
        containing all necessary interactive commands for annotation.

        :param qidata_object: object to display
        """
        QWidget.__init__(self, parent)

        ## VIEW DEFINITION

        # First widget layer: annotation selector
        self.annotation_selector_widget = QComboBox(self)
        self.annotation_selector_widget.setEnabled(True)
        self.annotation_selector_widget.currentIndexChanged['QString'].connect(self.userChanged.emit)

        # Second widget layer: specialized qidata_widget
        self.qidata_widget = QiDataWidget(qidata_object)
        self.qidata_widget.newMetadataAdditionRequested.connect(self.newMetadataAdditionRequested.emit)
        self.qidata_widget.metadataTypeChangeRequested.connect(self.metadataTypeChangeRequested.emit)

        # Main layout
        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.addWidget(self.annotation_selector_widget)
        self.main_vlayout.addWidget(self.qidata_widget)
        self.setLayout(self.main_vlayout)

    # ───────
    # Methods

    def addObject(self, coordinates):
        __doc__ = QiDataWidget.addMetadataToView.__doc__
        return self.qidata_widget.addMetadataToView(coordinates)

    def displayObject(self, qidata_object):
        __doc__ = QiDataWidget.displayMetadataDetails.__doc__
        self.qidata_widget.displayMetadataDetails(qidata_object)

    def askForItemDeletion(self, item):
        """
        Ask the user confirmation to remove the given item

        :param item:  Reference to the widget
        :return: True if the item was deleted, False otherwise
        """
        response = QMessageBox.warning(self, "Suppression", "Are you sure you want to remove this annotation ?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            self.qidata_widget.removeMetadataFromView(item)
            return True
        return False

    def askForDataSave(self):
        """
        Ask the user if the metadata must be saved

        This typically happens when the user selected a new file to open
        :return: The user's response
        :rtype: ``PySide.QtGui.QMessageBox``
        """
        response = QMessageBox.warning(self, "Leaving..", "You are about to leave this file. Do you want to save your modifications ?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        return response
