# -*- coding: utf-8 -*-

# Qt
from PySide.QtCore import Signal
from PySide.QtGui import QWidget, QHBoxLayout, QVBoxLayout

# qidata
from metadata_details import MetadataDetails
from general_metadata_list import GeneralMetadataList
from qidata.types import CheckCompatibility, MetadataType
from metadata_items.list_item import MetadataListItem
import data_widgets

class MainWidget(QWidget):
    """
    General widget for QiData GUI applications.

    Contains three subwidgets, one to display MetadataObjects information,
    a second to show metadata that is not localized on data, and a third
    specialized in the data displayed (image, audio, ...).
    """

    # ────────────
    # Data Widgets

    LOOKUP_WIDGET_MODEL = {
        "Image": data_widgets.ImageWidget,
    }

    # ───────
    # Signals

    # User asked for a metadata object to be added at location given in parameter
    objectAdditionRequired = Signal(list)

    # User requested to change the type of the selected metadata object
    objectTypeChangeRequested = Signal([MetadataType])

    # ───────────
    # Constructor

    def __init__(self, data_object, parent=None):
        """
        MainWidget constructor

        :param data_object:  QiDataObject to display (qidata.qidataobject.QiDataObject)
        :param parent:  Parent of this widget
        """
        super(MainWidget, self).__init__(parent)

        ## VIEW DEFINITION

        # Main widget
        try:
            self.main_widget = self.LOOKUP_WIDGET_MODEL[str(data_object.type)](data_object.raw_data)
        except KeyError:
            raise TypeError("%s is not supported"%data_object)
        self.main_widget.setParent(self)

        # Bind main widget's signals
        self.main_widget.objectAdditionRequired.connect(self.objectAdditionRequired.emit)

        # Right panel widget
        self.right_panel_widget = QWidget(self)

        # Widget displaying annotations concerning the whole file / image / sound / ...
        self.overall_annotations_displayer_widget = GeneralMetadataList(self.right_panel_widget)
        self.overall_annotations_displayer_widget.objectAdditionRequired.connect(self.objectAdditionRequired)

        # Object displaying widget
        self.object_displaying_widget = MetadataDetails(CheckCompatibility.getCompatibleMetadataTypes(data_object.type), self)
        self.object_displaying_widget.objectTypeChangeRequested.connect(lambda type_name: self.objectTypeChangeRequested.emit(MetadataType[type_name]))

        # Right layout
        self.right_panel_layout = QVBoxLayout(self)
        self.right_panel_layout.addWidget(self.overall_annotations_displayer_widget)
        self.right_panel_layout.addWidget(self.object_displaying_widget)
        self.right_panel_widget.setLayout(self.right_panel_layout)

        # Main layout
        self.main_hlayout = QHBoxLayout(self)
        self.main_hlayout.addWidget(self.main_widget)
        self.main_hlayout.addWidget(self.right_panel_widget)
        self.setLayout(self.main_hlayout)

    # ───────
    # Methods

    def addMetadataObjectToView(self, coordinates):
        """
        Add an object to display on the view.

        This method only adds the object on the specialized widget but
        does not display the object details.

        :param coordinates:  Coordinates of the object to show (format depends on data type)
        :return:  Reference to the widget representing the object

        .. note::
            The returned reference is handy to connect callbacks on the
            widget signals. This reference is also needed to remove the object.
        """
        if coordinates is None:
            return self.overall_annotations_displayer_widget.addObject()
        else:
            return self.main_widget.addObject(coordinates)

    def displayMetadataObjectDetails(self, metadata_object):
        """
        Display the object details

        This method only displays the object details in the corresponding widget
        but does not add the object on the specialized widget.

        :param metadata_object:  QiDataObject to display
        """
        self.object_displaying_widget.displayObject(metadata_object)

    def removeMetadataObject(self, item):
        """
        Remove an object from the widget

        This method removes the object from the specialized view and clears the
        object viewing panel.

        :param item:  Reference to the widget
        """
        if type(item) == MetadataListItem:
            self.overall_annotations_displayer_widget.removeItem(item)
        else:
            self.main_widget.removeItem(item)
        self.object_displaying_widget.clearObject()

