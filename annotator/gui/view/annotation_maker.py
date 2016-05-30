# -*- coding: utf-8 -*-

from .editable_tree import EditableTree

from PySide.QtGui import QWidget, QVBoxLayout, QComboBox
from PySide.QtCore import Signal

import qidata_objects

class AnnotationMaker(QWidget):

    # ───────
    # Signals

    messageTypeChangeRequested = Signal(str)

    # ───────────
    # Constructor

    def __init__(self):
        super(AnnotationMaker, self).__init__()

        ## VIEW DEFINITION

        # Top layer widget: annotation definition
        self.definition_widget = QWidget(self)

        self.annotation_type_selection_widget = QComboBox(self.definition_widget)
        self.annotation_type_selection_widget.setEnabled(False)

        self.topic_vlayout = QVBoxLayout(self)
        self.topic_vlayout.addWidget(self.annotation_type_selection_widget)

        self.definition_widget.setLayout(self.topic_vlayout)

        # Middle widget: annotation composition
        self.editable_tree = EditableTree(self)

        # Integrate all the widgets and the top layer widget into the main layout
        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.addWidget(self.definition_widget)
        self.main_vlayout.addWidget(self.editable_tree)
        self.setLayout(self.main_vlayout)

        ## GUI ELEMENT SETUP

        # Topic selection
        self.annotation_type_selection_widget.addItems(qidata_objects.DataObjectTypes) # we add some message type
        self.annotation_type_selection_widget.currentIndexChanged['QString'].connect(self._handle_message_selected)

    # ──────────
    # Properties

    @property
    def msg(self):
        return self.editable_tree.message

    @msg.setter
    def msg(self, new_msg):
        self.editable_tree.message = new_msg

    # ───────
    # Methods

    def displayMessage(self, new_msg):
        # Enable type selector widget
        self.annotation_type_selection_widget.setEnabled(True)

        # Add message to the editable tree
        self.msg = new_msg

        # Set the selector to the type we just received (this will raise an event...)
        index = self.annotation_type_selection_widget.findText(type(new_msg).__name__)
        self.annotation_type_selection_widget.setCurrentIndex(index)

    def clearMessage(self):
        # Disable type selector widget
        self.annotation_type_selection_widget.setEnabled(False)

        # Remove message in the editable tree
        self.msg = None

    # ─────
    # Slots

    def _handle_message_selected(self, message_name):
        if message_name != '' and message_name != type(self.msg).__name__:
            # If the message name received is the same as the message type, do nothing
            self.messageTypeChangeRequested.emit(message_name)
