# -*- coding: utf-8 -*-

from PySide.QtGui import QWidget, QVBoxLayout, QListWidget, QPushButton
from PySide.QtCore import Signal

from metadata_items.list_item import MetadataListItem

class GeneralMetadataList(QWidget):
    """
    Widget to handle annotations concerning the whole file
    """

    # ───────
    # Signals

    #: User asked for a metadata object to be added
    objectAdditionRequired = Signal(list)

    # ───────────
    # Constructor

    def __init__(self, parent=None):
        """
        GeneralMetadataList constructor

        @parent       :  Parent of this widget
        """
        super(GeneralMetadataList, self).__init__(parent)

        ## VIEW DEFINITION

        self.annotations_list = QListWidget(self)
        self.addition_button = QPushButton("Add annotation", self)
        self.deletion_button = QPushButton("Delete annotation", self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.annotations_list)
        self.layout.addWidget(self.addition_button)
        self.layout.addWidget(self.deletion_button)
        self.setLayout(self.layout)

        ## GUI ELEMENT SETUP

        self.addition_button.clicked.connect(lambda: self.objectAdditionRequired.emit(None))
        self.deletion_button.clicked.connect(lambda: self.annotations_list.currentItem().suppressionRequired.emit())
        self.annotations_list.itemClicked.connect(lambda item: item.isSelected.emit())

        self.counter = 0

    # ───────
    # Methods

    def addObject(self):
        """
        Add an object to display on the view.

        @return      :  Reference to the widget representing the object

        ..note:: The returned reference is handy to connect callbacks on the
        widget signals. This reference is also needed to remove the object.
        """
        if self.annotations_list.count() == 0:
            self.counter = 1
        else:
            self.counter += 1
        return MetadataListItem("annotation_%d"%self.counter, self.annotations_list)

    def removeItem(self, item):
        """
        Remove item from the list

        @item  :  Item to remove
        """
        if self.annotations_list.row(item) == self.annotations_list.count()-1:
            self.counter -= 1
        self.annotations_list.takeItem(self.annotations_list.row(item))