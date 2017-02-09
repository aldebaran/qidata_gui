# -*- coding: utf-8 -*-

# Qt
from PySide import QtGui

# local
from raw_data_widget import RawDataWidgetInterface
from ..metadata_items import MetadataBaseItem

class AudioWidget(RawDataWidgetInterface, QtGui.QWidget):
    """
    Widget specialized in displaying audio with Metadata Objects
    """

    # ───────────
    # Constructor

    def __init__(self, audio_raw_data, parent=None):
        """
        AudioWidget constructor

        :param audio_raw_data:  Audio raw data
        :param parent:  Parent of this widget
        """
        QtGui.QWidget.__init__(self, parent)

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

    # ───────────────
    # Private methods

    def _locationToCoordinates(self, location):
        if coordinates is not None:
            # TODO: create a metadata object suited for audio
            return
        else:
            return None