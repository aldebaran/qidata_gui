# -*- coding: utf-8 -*-

# Qt
from PySide.QtGui import QWidget
from PySide.QtCore import Signal

from ..metadata_items import MetadataBaseItem

class AudioWidget(QWidget):
    """
    Widget specialized in displaying audio with Metadata Objects
    """

    # ───────
    # Signals

    objectAdditionRequired = Signal(list)

    # ───────────
    # Constructor

    def __init__(self, audio_raw_data, parent=None):
        """
        AudioWidget constructor

        :param audio_raw_data:  Audio raw data
        :param parent:  Parent of this widget
        """
        super(AudioWidget, self).__init__(parent)

    # ───────
    # Methods

    def addObject(self, coordinates):
        """
        Add a metadata object to display on the view.

        :param coordinates:  Coordinates of the object to show (format depends on data type)
        :return:  Reference to the widget representing the object

        .. note::
            The returned reference is handy to connect callbacks on the
            widget signals. This reference is also needed to remove the object.
        """
        r = MetadataBaseItem()
        return r

    def removeItem(self, item):
        """
        Remove an object from the widget

        :param item:  Reference to the widget
        """
        return