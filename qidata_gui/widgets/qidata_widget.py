# -*- coding: utf-8 -*-

# Qt
from PySide.QtCore import Signal
from PySide.QtGui import QWidget, QHBoxLayout, QVBoxLayout

# qidata
from metadata_details import MetadataDetails
from general_metadata_list import GeneralMetadataList
from qidata import MetadataType
from metadata_items.list_item import MetadataListItem
import data_widgets

class QiDataWidget(QWidget):
    """
    General widget to display QiDataObject.

    Contains three subwidgets:
        - one specialized in the data displayed, which also shows metadata locations
        - one showing the list of unlocalized metadata
        - one displaying the selected metadata content and allowing to update it
    """

    # ────────────
    # Data Widgets

    LOOKUP_WIDGET_MODEL = {
        "IMAGE": data_widgets.ImageWidget,
        "AUDIO": data_widgets.AudioWidget,
        "DATASET": data_widgets.DataSetWidget,
    }

    # ───────
    # Signals

    # User asked for a metadata object to be added at location given in parameter
    newMetadataAdditionRequested = Signal(list)

    # User requested to change the type of the selected metadata object
    metadataTypeChangeRequested = Signal([MetadataType])

    # ───────────
    # Constructor

    def __init__(self, data_object, parent=None):
        """
        QiDataWidget constructor

        :param data_object:  QiDataObject to display (``qidata.QiDataObject``)
        :param parent:  Parent of this widget (``PySide.QtGui.QWidget``)
        """
        QWidget.__init__(self, parent)
        self.displayed_object = data_object

    # ───────────────
    # Private methods

    def _show(self):

        # ───────────────
        # VIEW DEFINITION

        # ──────────
        # Left panel

        # Raw data viewer creation
        try:
            self.raw_data_viewer = self.LOOKUP_WIDGET_MODEL[str(self.displayed_object.type)](self.displayed_object.raw_data)
            self.raw_data_viewer.setParent(self)
        except KeyError:
            raise TypeError("No existing widget for the following type of QiDataObject: %s"%str(self.displayed_object.type))

        # ───────────
        # Right panel

        # Containing widget
        self.right_panel_widget = QWidget(self)

        # Widget displaying annotations concerning the whole object
        self.overall_annotations_displayer_widget = GeneralMetadataList(self.right_panel_widget)

        # Metadata displaying widget
        self.object_displaying_widget = MetadataDetails(list(MetadataType), self)

        # Insert all widgets in their layouts
        self.right_panel_layout = QVBoxLayout(self)
        self.right_panel_layout.addWidget(self.overall_annotations_displayer_widget)
        self.right_panel_layout.addWidget(self.object_displaying_widget)
        self.right_panel_widget.setLayout(self.right_panel_layout)

        # ─────────────────────────────────
        # Insert both panels in main widget

        self.main_hlayout = QHBoxLayout(self)
        self.main_hlayout.addWidget(self.raw_data_viewer)
        self.main_hlayout.addWidget(self.right_panel_widget)
        self.setLayout(self.main_hlayout)

        # ────────────
        # Bind signals

        self.raw_data_viewer.objectAdditionRequired.connect(self.newMetadataAdditionRequested.emit)
        self.overall_annotations_displayer_widget.objectAdditionRequired.connect(self.newMetadataAdditionRequested)
        self.object_displaying_widget.objectTypeChangeRequested.connect(lambda type_name: self.metadataTypeChangeRequested.emit(MetadataType[type_name]))

    # ───────
    # Methods

    def addMetadataToView(self, coordinates):
        """
        Add a metadata item on the view.

        This method adds an item representing the metadata location but
        does not display the object details.

        :param coordinates:  Coordinates of the object to show (format depends on data type)
        :return:  Reference to the widget representing the metadata

        .. note::
            ``coordinates`` can be ``None`` in which case the metadata is considered
            as `unlocalized`.

        .. note::
            The returned reference is handy to connect callbacks on the
            widget signals. This reference is also needed to remove the object.
        """
        if coordinates is None:
            return self.overall_annotations_displayer_widget.addObject()
        else:
            return self.raw_data_viewer.addObject(coordinates)

    def displayMetadataDetails(self, metadata_object):
        """
        Display the object details

        This method only displays the object details in the corresponding widget
        but does not add the object on the specialized widget.

        :param metadata_object:  QiDataObject to display
        """
        self.object_displaying_widget.displayObject(metadata_object)

    def removeMetadataFromView(self, item):
        """
        Remove a metadata item from the widget

        This method removes the item representing the metadata and clears the
        widget showing metadata details.

        :param item:  Reference to the widget
        """
        if type(item) == MetadataListItem:
            self.overall_annotations_displayer_widget.removeItem(item)
        else:
            self.raw_data_viewer.removeItem(item)
        self.object_displaying_widget.clearObject()

    # ──────────
    # Properties

    @property
    def displayed_object(self):
        return self._displayed_object

    @displayed_object.setter
    def displayed_object(self, new_object):
        self._displayed_object = new_object
        self._show()
