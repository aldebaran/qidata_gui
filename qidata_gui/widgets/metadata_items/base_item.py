# -*- coding: utf-8 -*-

from PySide.QtCore import Signal, QObject, Qt

class MetadataBaseItem(QObject):
    """
    Item to show the presence of an metadata object
    """

    # ───────
    # Signals

    isSelected = Signal()
    isMoved = Signal(list)
    isResized = Signal(list)
    suppressionRequired = Signal()

    # ──────────
    # Contructor

    def __init__(self, parent=None):
        """
        MetadataBaseItem constructor

        @parent       :  Parent of this widget
        """
        super(MetadataBaseItem, self).__init__(parent)

    # ───────
    # Methods

    def select(self):
        """
        Select this item
        """
        self.setSelected(True)