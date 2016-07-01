# -*- coding: utf-8 -*-

# Qt
from PySide.QtCore import Signal
from PySide.QtGui import QWidget, QHBoxLayout

# qidata
from qidata_objects_displayer import QiDataObjectDisplayer

class QiDataWidget(QWidget):
    """
    General widget for QiData GUI applications.

    Contains two subwidgets, one to display QiDataObjects information,
    and another specialized in the data displayed (image, audio, ...).
    """

    # ───────
    # Signals

    objectAdditionRequired = Signal(list)
    objectTypeChangeRequested = Signal(str)

    # ───────────
    # Constructor

    def __init__(self, qidata_subwidget, parent=None):
        """
        QiDataWidget constructor

        @qidata_subwidget  :  Data specialized widget to use
        @parent            :  Parent of this widget
        """
        super(QiDataWidget, self).__init__(parent)

        ## VIEW DEFINITION

        # Main widget
        self.main_widget = qidata_subwidget
        self.main_widget.setParent(self)

        # Bind main widget's signals
        self.main_widget.objectAdditionRequired.connect(self.objectAdditionRequired.emit)

        # Object displaying widget
        self.object_displaying_widget = QiDataObjectDisplayer(self)
        self.object_displaying_widget.objectTypeChangeRequested.connect(self.objectTypeChangeRequested.emit)

        # Main layout
        self.main_hlayout = QHBoxLayout(self)
        self.main_hlayout.addWidget(self.main_widget)
        self.main_hlayout.addWidget(self.object_displaying_widget)
        self.setLayout(self.main_hlayout)

    # ───────
    # Methods

    def addObject(self, coordinates):
        """
        Add an object to display on the view.

        This method only add the object on the specialized widget but
        does not display the object details in the corresponding widget.

        @coordinates :  Coordinates of the object to show (format depends on data type)
        @return      :  Reference to the widget representing the object

        ..note:: The returned reference is handy to connect callbacks on the
        widget signals. This reference is also needed to remove the object.
        """
        return self.main_widget.addObject(coordinates)

    def displayObject(self, qidata_object):
        """
        Display the object details

        This method only display the object details in the corresponding widget
        but does not add the object on the specialized widget.

        @qidata_object  :  QiDataObject to display
        """
        self.object_displaying_widget.displayObject(qidata_object)

    def removeObject(self, item):
        """
        Remove an object from the widget

        This method removes the object from the specialized view and clears the
        object viewing panel.

        @item  :  Reference to the widget
        """
        self.main_widget.removeItem(item)
        self.object_displaying_widget.clearObject()

    