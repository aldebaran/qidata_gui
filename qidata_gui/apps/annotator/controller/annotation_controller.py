# -*- coding: utf-8 -*-

# Standard library
import copy

# Qt
from PySide.QtCore import QObject, Signal
from PySide.QtGui import QMessageBox

# qidata
from qidata import qidatafile
from qidata import MetadataType, makeMetadataObject

# local
from .. import exceptions
from ..view import AnnotationInterface

class AnnotationController(QObject):
    """
    Sub-controller of the annotation maker tool. It handles the annotation
    on one specific QiDataObject. It is the `controller` part of an MVC pattern,
    the model being the QiDataFile/QiDataSet and the view being the
    ``AnnotationInterface``.
    """

    # ───────────
    # Constructor

    def __init__(self, source_path, user_name):
        QObject.__init__(self)

        # Load information from the given file
        self.source_path = source_path
        self._loadFileInformation()

        # Add annotators to the corresponding list
        # If user is not already in it, add it
        self.view.annotation_selector_widget.addItems(self.annotators)
        if not user_name in self.annotators:
            self.view.annotation_selector_widget.addItem(user_name)

        # And then select it
        self.view.annotation_selector_widget.setCurrentIndex(
            self.view.annotation_selector_widget.findText(user_name)
        )

        # Store references to metadata display items
        self.item_reference_to_metadata_map = dict()

        # Load only requested annotations
        self.onUserChanged(user_name)

        # Keep track of user's action
        self.last_selected_item_index = None
        self.last_selected_item_type = list(MetadataType)[0]

        # Connect view's callbacks
        self.view.newMetadataAdditionRequested.connect(self.onAnnotationAdditionRequest)
        self.view.metadataTypeChangeRequested.connect(self.onTypeChangeRequest)
        self.view.userChanged.connect(self.onUserChanged)

    # ──────────────
    # Public methods

    def addAnnotationItems(self, annotationsToAdd):
        for annotationIndex in range(0,len(annotationsToAdd)):

            # Add to general model
            self.metadata[self.user_name][type(annotationsToAdd[annotationIndex][0]).__name__].append(annotationsToAdd[annotationIndex])

            # Add to the view
            self._addAnnotationItemOnView(annotationsToAdd[annotationIndex])

    # ───────────────
    # Private methods

    def _loadFileInformation(self):
        # Retrieve information from the source object
        with qidatafile.open(self.source_path, "r") as _file:
            self.annotators = _file.annotators
            self.metadata = _file.metadata
            self.view = AnnotationInterface(_file)

    def _cleanEmptyElements(self, metadata):
        out = copy.deepcopy(metadata)
        for supported_metadata_type in list(MetadataType):
            if out[self.user_name][str(supported_metadata_type)] == []:
                out[self.user_name].pop(str(supported_metadata_type))
        if out[self.user_name] == dict():
            out.pop(self.user_name)
        return out

    def _saveFileInformation(self):
        with qidatafile.open(self.source_path, "w") as _file:
                _file.metadata = self._cleanEmptyElements(self.metadata)

    def _loadUserAnnotations(self, user_name):
        self.user_name = user_name
        if not user_name in self.annotators:
            self.metadata[user_name] = dict()
        for supported_metadata_type in list(MetadataType):
            if not str(supported_metadata_type) in self.metadata[user_name].keys():
                self.metadata[user_name][str(supported_metadata_type)] = []

    def _showAnnotations(self):
        # Clear
        for existing_item in self.item_reference_to_metadata_map:
            self.view.qidata_widget.removeMetadataFromView(existing_item)
        self.item_reference_to_metadata_map = dict()
        # Display
        for m in [j for v in list(MetadataType) for j in self.metadata[self.user_name][str(v)]]:
            self._addAnnotationItemOnView(m)

    def _addAnnotationItemOnView(self, annotation_item):
        r = self.view.addObject(annotation_item[1])
        r.isSelected.connect(lambda:self.onItemSelected(r))
        r.isMoved.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.isResized.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.suppressionRequired.connect(lambda: self.onAnnotationDeletionRequest(r))
        self.item_reference_to_metadata_map[r] = annotation_item
        return r

    def _makeLocation(self, coordinates):
        """
        Must be overriden by child classes
        """
        raise NotImplementedError

    # ─────
    # Slots

    def onAnnotationAdditionRequest(self, coordinates):
        # Create new item
        loc = self._makeLocation(coordinates)
        new_annotation = [makeMetadataObject(self.last_selected_item_type),loc]

        # Add annotation to metadata
        self.metadata[self.user_name][str(self.last_selected_item_type)].append(new_annotation)

        # Display it on the qidata widget
        r = self._addAnnotationItemOnView(new_annotation)

        # Display information on it in data editor widget
        r.select()

    def onItemSelected(self, item):
        self.last_selected_item = item
        self.last_selected_item_type = MetadataType[type(self.item_reference_to_metadata_map[item][0]).__name__]
        self.view.displayObject(self.item_reference_to_metadata_map[item][0])

    def onItemCoordinatesChange(self, item, coordinates):
        # This will also affect the real model as it is a pointer
        self.item_reference_to_metadata_map[item][1] = coordinates

    def onTypeChangeRequest(self, message_type):
        # Retrieve the current type of the annotation
        old_message_type = self.last_selected_item_type

        # Remove annotation from its former category in model, and add it to the new one
        self.metadata[self.user_name][str(old_message_type)].remove(self.item_reference_to_metadata_map[self.last_selected_item])
        self.metadata[self.user_name][str(message_type)].append(self.item_reference_to_metadata_map[self.last_selected_item])

        # Then change the annotation type in the metadata_as_list (this will also be done in model because
        # it's a pointer)
        self.item_reference_to_metadata_map[self.last_selected_item][0] = makeMetadataObject(message_type)

        # Register the current message type and send the selection signal as usual
        self.last_selected_item_type = message_type
        self.view.displayObject(self.item_reference_to_metadata_map[self.last_selected_item][0])

    def onAnnotationDeletionRequest(self, item):
        if self.view.askForItemDeletion(item):
            self.last_selected_item_index = None
            annotation = self.item_reference_to_metadata_map.pop(item)
            self.metadata[self.user_name][type(annotation[0]).__name__].remove(annotation)

    def onUserChanged(self, user_name):
        self._loadUserAnnotations(user_name)
        self._showAnnotations()

    def onExit(self, auto_save):
        savingRequest = (QMessageBox.Yes if auto_save else self.view.askForDataSave())
        if savingRequest == QMessageBox.Yes:
            self._saveFileInformation()
        if savingRequest == QMessageBox.Cancel:
            raise exceptions.SelectionChangeCanceledByUser()
