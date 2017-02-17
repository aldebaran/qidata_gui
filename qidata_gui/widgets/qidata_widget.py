# -*- coding: utf-8 -*-

# Qt
from PySide import QtCore, QtGui

# qidata
from qidata import MetadataType, makeMetadataObject, qidatafile

# local
from metadata_details import MetadataDetails
from general_metadata_list import GeneralMetadataList
from annotators_ticking_list import AnnotatorsTickingList
from metadata_items.list_item import MetadataListItem
from data_widgets import makeRawDataWidget
import exceptions

# ────────────────
# Local Decorators

def raiseIfReadOnly(f):
    def wrapper(self, *args):
        if self.read_only:
            raise exceptions.AttributeIsReadOnly()
        else:
            return f(self, *args)
    return wrapper

def raiseIfWrongAnnotator(f):
    def wraps(self, annotation, *args):
        try:
            self.metadata[self.writer][type(annotation[0]).__name__].index(annotation)
        except ValueError:
            raise exceptions.AttributeIsReadOnly()
        else:
            return f(self, annotation, *args)
    return raiseIfReadOnly(wraps)

def ignoreIfReadOnly(f):
    def wrapper(self, *args):
        if self.read_only:
            return
        else:
            return f(self, *args)
    return wrapper

def ignoreIfWrongAnnotator(f):
    def wraps(self, item, *args):
        annotation = self.item_reference_to_metadata_map[item]
        try:
            self.metadata[self.writer][type(annotation[0]).__name__].index(annotation)
        except ValueError:
            self._removeMetadataFromView(item)
            self._addAnnotationItemOnView(annotation).select()
        else:
            return f(self, item, *args)
    return ignoreIfReadOnly(wraps)

# ────────────
# QiDataWidget

class QiDataWidget(QtGui.QWidget):
    """
    General widget to display QiDataObject.

    Contains four subwidgets:
        - one specialized in the data displayed, which also shows metadata locations
        - one showing the list of unlocalized metadata
        - one displaying the selected metadata content and allowing to update it
        - one allowing to select the annotators whose annotations are visible
    """

    # ───────────
    # Constructor

    def __init__(self, source_path, writer=None, parent=None):
        """
        QiDataWidget constructor

        :param source_path:  Path to the ``QiDataObject`` to display
        :param parent:  Parent of this widget (``PySide.QtGui.QWidget``)
        :param writer: The name of the person modifying the metadata. Sending None or
        \"\" will result in file being displayed in read-only mode.
        """
        QtGui.QWidget.__init__(self, parent)

        # Load information from the given file
        self.source_path = source_path
        self.writer = writer
        self._read_only = (writer in [None, ""])
        self._loadFileInformation()

        # Store references to metadata display items
        self.item_reference_to_metadata_map = dict()

        # Keep track of user's action
        self.last_selected_item_index = None
        self.last_selected_item_type = list(MetadataType)[0]
        self._showAnnotations(self.annotators)

    # ──────────
    # Properties

    @property
    def displayed_object(self):
        return self._displayed_object

    @displayed_object.setter
    def displayed_object(self, new_object):
        self._displayed_object = new_object
        self._createView()

    @property
    def read_only(self):
        return self._read_only

    @read_only.setter
    def read_only(self, new_read_only):
        # For now property is useless
        # But later on, the change will have to be propagated to
        # children widgets
        self._read_only = new_read_only

    # ──────────
    # Public API

    @raiseIfReadOnly
    def addAnnotationItem(self, annotation_to_add):
        # Add to general model
        self.metadata[self.writer][type(annotation_to_add[0]).__name__].append(annotation_to_add)

        # Add to the view
        r = self._addAnnotationItemOnView(annotation_to_add)

        # Display information on it in data editor widget
        r.select()

    @raiseIfReadOnly
    def addAnnotationItems(self, annotations_to_add):
        for annotationIndex in range(0,len(annotations_to_add)):

            # Add to general model
            self.metadata[self.writer][type(annotations_to_add[annotationIndex][0]).__name__].append(annotations_to_add[annotationIndex])

            # Add to the view
            self._addAnnotationItemOnView(annotations_to_add[annotationIndex])

    @raiseIfWrongAnnotator
    def changeAnnotationType(self, annotation, new_type_name):
        # Remove annotation from metadata
        self.metadata[self.writer][type(annotation[0]).__name__].remove(annotation)

        # Then change the annotation object
        annotation[0] = makeMetadataObject(new_type_name)

        # Finally, add it back to the metadata, in the new category
        self.metadata[self.writer][str(new_type_name)].append(annotation)

    # ─────
    # Slots

    @ignoreIfReadOnly
    def onAnnotationAdditionRequest(self, coordinates):
        # Create new item
        loc = self.raw_data_viewer._locationToCoordinates(coordinates)
        new_annotation = [makeMetadataObject(self.last_selected_item_type),loc]

        # Add annotation to metadata
        self.addAnnotationItem(new_annotation)

    def onTypeChangeRequest(self, item, message_new_type):
        try:
            self.changeAnnotationType(self.item_reference_to_metadata_map[item], message_new_type)
        except exceptions.AttributeIsReadOnly:
            print "Read-only, cannot change type"
        else:
            # Register the current message type and send the selection signal as usual
            self.last_selected_item_type = message_new_type
        finally:
            self._displayMetadataDetails(self.item_reference_to_metadata_map[item][0])

    def onItemSelected(self, item):
        self.last_selected_item = item
        self.last_selected_item_type = MetadataType[type(self.item_reference_to_metadata_map[item][0]).__name__]
        annotation = self.item_reference_to_metadata_map[item]
        try:
            self.metadata[self.writer][type(annotation[0]).__name__].index(annotation)
        except ValueError:
            self.object_displaying_widget.object_display_widget.read_only = True
        else:
            self.object_displaying_widget.object_display_widget.read_only = False
        self._displayMetadataDetails(self.item_reference_to_metadata_map[item][0])

    @ignoreIfWrongAnnotator
    def onItemCoordinatesChange(self, item, coordinates):
        # Find corresponding annotation
        annotation = self.item_reference_to_metadata_map[item]

        # Change annotation's coordinates
        annotation[1] = coordinates

    @ignoreIfWrongAnnotator
    def onAnnotationDeletionRequest(self, item):
        # Ask the user confirmation to remove the given item
        response = QtGui.QMessageBox.warning(self,
                                             "Suppression",
                                             "Are you sure you want to remove this annotation ?",
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            self.last_selected_item_index = None

            # Pop annotation out of item <-> annotation mapping
            annotation = self.item_reference_to_metadata_map[item]

            # Remove item from the view
            self._removeMetadataFromView(item)

            # Remove annotation from metadata
            self.metadata[self.writer][type(annotation[0]).__name__].remove(annotation)

    @raiseIfReadOnly
    def onExit(self, auto_save):
        # Ask the user if the metadata must be saved
        if auto_save:
            savingRequest = QtGui.QMessageBox.Yes
        else:
            savingRequest = QtGui.QMessageBox.warning(self,
                                                      "Leaving..",
                                                      "You are about to leave this file. Do you want to save your modifications ?",
                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
        if savingRequest == QtGui.QMessageBox.Yes:
            self._saveFileInformation()
        if savingRequest == QtGui.QMessageBox.Cancel:
            raise exceptions.UserCancelation()

    # ───────────────
    # Private methods

    def _loadFileInformation(self):
        # Retrieve information from the source object
        with qidatafile.open(self.source_path, "r") as _file:
            self.annotators = _file.annotators
            self.annotators.sort()
            if self.writer in self.annotators:
                self.annotators.remove(self.writer)
            if not self.read_only:
                self.annotators.insert(0, self.writer)
            self.metadata = _file.metadata
            self.displayed_object = _file

        if not self.read_only:
            self._allocateSpaceForUserAnnotations(self.writer)

    @raiseIfReadOnly
    def _saveFileInformation(self):
        self._deallocateUnusedSpaceForUserAnnotations()
        with qidatafile.open(self.source_path, "w") as _file:
                _file.metadata = self.metadata
        self._allocateSpaceForUserAnnotations(self.writer)

    @raiseIfReadOnly
    def _allocateSpaceForUserAnnotations(self, user_name):
        if not user_name in self.metadata.keys():
            self.metadata[user_name] = dict()
        for supported_metadata_type in list(MetadataType):
            if not str(supported_metadata_type) in self.metadata[user_name].keys():
                self.metadata[user_name][str(supported_metadata_type)] = []

    @raiseIfReadOnly
    def _deallocateUnusedSpaceForUserAnnotations(self):
        for supported_metadata_type in list(MetadataType):
            if self.metadata[self.writer][str(supported_metadata_type)] == []:
                self.metadata[self.writer].pop(str(supported_metadata_type))
        if self.metadata[self.writer] == dict():
            self.metadata.pop(self.writer)

    def _createView(self):

        # ───────────────
        # VIEW DEFINITION

        # ──────────
        # Left panel

        # Raw data viewer creation
        try:
            self.raw_data_viewer = makeRawDataWidget(self.displayed_object)
            self.raw_data_viewer.setParent(self)
        except KeyError:
            raise TypeError("No existing widget for the following type of QiDataObject: %s"%str(self.displayed_object.type))

        # ───────────
        # Right panel

        # Containing widget
        self.right_panel_widget = QtGui.QWidget(self)

        # Widget displaying annotations concerning the whole object
        self.overall_annotations_displayer_widget = GeneralMetadataList(self.right_panel_widget)

        # Metadata displaying widget
        self.object_displaying_widget = MetadataDetails(list(MetadataType), self)

        # Insert all widgets in their layouts
        self.right_panel_layout = QtGui.QVBoxLayout(self)
        self.right_panel_layout.addWidget(self.overall_annotations_displayer_widget)
        self.right_panel_layout.addWidget(self.object_displaying_widget)
        self.right_panel_widget.setLayout(self.right_panel_layout)

        # New panel
        self.annotators_panel = AnnotatorsTickingList(not self.read_only, self.annotators)

        # ─────────────────────────────────
        # Insert both panels in main widget

        self.main_hlayout = QtGui.QHBoxLayout(self)
        self.main_hlayout.addWidget(self.raw_data_viewer)
        self.main_hlayout.addWidget(self.right_panel_widget)
        self.main_hlayout.addWidget(self.annotators_panel)
        self.setLayout(self.main_hlayout)

        # ────────────
        # Bind signals

        self.raw_data_viewer.objectAdditionRequired.connect(self.onAnnotationAdditionRequest)
        self.overall_annotations_displayer_widget.objectAdditionRequired.connect(self.onAnnotationAdditionRequest)
        self.object_displaying_widget.objectTypeChangeRequested.connect(lambda type_name: self.onTypeChangeRequest(self.last_selected_item, MetadataType[type_name]))
        self.annotators_panel.annotatorsTickedChanged.connect(self._showAnnotations)

    def _addAnnotationItemOnView(self, annotation_item):
        """
        Add a metadata item on the view.

        This method adds an item representing the metadata location but
        does not display the object details.

        :param annotation_item:  The item to be shown
        :return:  Reference to the widget representing the metadata

        .. note::
            The returned reference is handy to connect callbacks on the
            widget signals. This reference is also needed to remove the object.
        """
        if annotation_item[1] is None:
            r = self.overall_annotations_displayer_widget.addObject()
        else:
            r = self.raw_data_viewer.addObject(annotation_item[1])
        r.isSelected.connect(lambda:self.onItemSelected(r))
        r.isMoved.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.isResized.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.suppressionRequired.connect(lambda: self.onAnnotationDeletionRequest(r))
        self.item_reference_to_metadata_map[r] = annotation_item
        return r

    def _removeMetadataFromView(self, item):
        """
        Remove a metadata item from the widget

        This method removes the item representing the metadata and clears the
        widget showing metadata details.

        :param item:  Reference to the widget
        """
        self.item_reference_to_metadata_map.pop(item)
        if type(item) == MetadataListItem:
            self.overall_annotations_displayer_widget.removeItem(item)
        else:
            self.raw_data_viewer.removeItem(item)
        self.object_displaying_widget.clearObject()

    def _displayMetadataDetails(self, metadata_object):
        """
        Display the object details

        This method only displays the object details in the corresponding widget
        but does not add the object on the specialized widget.

        :param metadata_object:  QiDataObject to display
        """
        self.object_displaying_widget.displayObject(metadata_object)

    def _showAnnotations(self, annotators):
        # Clear
        for existing_item in list(self.item_reference_to_metadata_map):
            self._removeMetadataFromView(existing_item)
        self.item_reference_to_metadata_map = dict()
        # Display
        for m in [j for a in annotators if a in self.metadata.keys() for v in self.metadata[a].values() for j in v]:
            self._addAnnotationItemOnView(m)
