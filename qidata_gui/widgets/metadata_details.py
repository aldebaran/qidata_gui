
# -*- coding: utf-8 -*-

from PySide.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit
from PySide.QtCore import Signal

from strong_typing import ObjectDisplayWidget

import qidata.metadata_objects

class MetadataDetails(QWidget):
    """
    Widget to display MetadataObjects detailed information
    """

    # ───────
    # Signals

    objectTypeChangeRequested = Signal(str)

    # ───────────
    # Constructor

    def __init__(self, supported_metadata_type_list, parent=None):
        """
        MetadataDetails constructor

        :param supported_metadata_type_list: list of metadata types compatible
        with the represented data type
        :param parent:  Parent of this widget
        """
        super(MetadataDetails, self).__init__(parent)

        ## VIEW DEFINITION

        # First widget: data type selection
        self.selection_widget = QWidget(self)

        self.annotation_type_selection_widget = QComboBox(self.selection_widget)
        self.annotation_type_selection_widget.setEnabled(False)

        self.type_selection_vlayout = QVBoxLayout(self)
        self.type_selection_vlayout.addWidget(self.annotation_type_selection_widget)

        self.selection_widget.setLayout(self.type_selection_vlayout)

        # Second widget: data display
        self.object_display_widget = ObjectDisplayWidget(self)

        # Integrate all the widgets and the top layer widget into the main layout
        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.addWidget(self.selection_widget)
        self.main_vlayout.addWidget(self.object_display_widget)
        self.setLayout(self.main_vlayout)

        ## GUI ELEMENT SETUP

        # Topic selection
        for metadata_type in supported_metadata_type_list:
            self.annotation_type_selection_widget.addItem(str(metadata_type)) # we add some message type
        self.annotation_type_selection_widget.currentIndexChanged['QString'].connect(self._handle_message_selected)

    # ───────
    # Methods

    def displayObject(self, qidata_object):
        """
        Display the object details

        :param qidata_object:  QiDataObject to display
        """
        # Enable type selector widget
        self.annotation_type_selection_widget.setEnabled(True)

        # Add data to the editable tree
        self.object_display_widget.data = qidata_object

        # Set the selector to the type we just received (this will raise an event...)
        index = self.annotation_type_selection_widget.findText(type(qidata_object).__name__)
        self.annotation_type_selection_widget.setCurrentIndex(index)

    def clearObject(self):
        """
        Clear the widget
        """
        # Disable type selector widget
        self.annotation_type_selection_widget.setEnabled(False)

        # Remove data in the editable tree
        self.object_display_widget.data = None

    # ─────
    # Slots

    def _handle_message_selected(self, message_name):
        if message_name != '' and message_name != type(self.object_display_widget.data).__name__:
            # If the message name received is the same as the data type, do nothing
            self.objectTypeChangeRequested.emit(message_name)
