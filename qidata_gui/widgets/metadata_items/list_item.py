# -*- coding: utf-8 -*-

from PySide.QtGui import QListWidgetItem
from PySide.QtCore import Signal, QObject, Qt

from .base_item import MetadataBaseItem

class MetadataListItem(QListWidgetItem, MetadataBaseItem):
    """
    Item to show the presence of an object without location
    """

    # ───────
    # Signals

    isSelected = Signal()
    suppressionRequired = Signal()

    # ──────────
    # Contructor

    def __init__(self, name, parent=None):
        """
        QiDataObjectRectItem constructor

        @name         :  Text to display
        @parent       :  Parent of this widget
        """
        QListWidgetItem.__init__(self, name, view = parent)
        MetadataBaseItem.__init__(self, parent)

    # ───────
    # Methods

    def select(self):
        """
        Select this item
        """
        self.setSelected(True)
        self.isSelected.emit()

    # ─────────
    # Operators

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.text() == other.text()

    def __ne__(self, other):
        if type(other) != type(self):
            return True
        return self.text() != other.text()