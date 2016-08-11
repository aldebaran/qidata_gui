# -*- coding: utf-8 -*-

# Qt
from PySide.QtCore import Signal

# qidata
from qidata.files import qidatafile
from qidata_gui.widgets import makeWidget
from ..datacontroller import DataController
from ...view import CentralWidget
from qidata.metadata_objects import *
from qidata.types import CheckCompatibility

class ImageController(DataController):

    # ───────────
    # Constructor

    def __init__(self, source_path, user_name):
        super(ImageController, self).__init__()
        DataController.modelHandler = qidatafile.open(source_path, "w")
        DataController.widget = CentralWidget(DataController.modelHandler)
        DataController.widget.annotation_selector_widget.user_selector_widget.addItems(self.modelHandler.annotators)

        self.user_name = user_name
        self._loadUserAnnotations(self.user_name)

        if not user_name in self.modelHandler.annotators:
            DataController.widget.annotation_selector_widget.user_selector_widget.addItem(user_name)
        i=DataController.widget.annotation_selector_widget.user_selector_widget.findText(user_name)
        DataController.widget.annotation_selector_widget.user_selector_widget.setCurrentIndex(i)
        DataController.widget.userChanged.connect(self.onUserChanged)

        # Remember which item on the image widget was lastly selected
        self.last_selected_item_index = None

        # Remember which type was lastly required by user.
        # If none was required, use first annotation type
        self.last_selected_item_type = CheckCompatibility.getCompatibleMetadataTypes(self.modelHandler.type)[0]

        # Store created items in same order as annotations in local_model
        self.item_list = []

        self._showAnnotations()

        self.widget.objectAdditionRequired.connect(self.createNewItem)
        self.widget.objectTypeChangeRequested.connect(self.onTypeChangeRequest)

    # ───────
    # Methods

    def addAnnotationItemOnView(self, annotation_item):
        r = self.widget.addObject(annotation_item)
        r.isSelected.connect(lambda:self.onItemSelected(r))
        r.isMoved.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.isResized.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.suppressionRequired.connect(lambda: self.deleteAnnotation(r))
        self.item_list.append(r)
        return r

    def addAnnotationItems(self, annotationsToAdd):
        for annotationIndex in range(0,len(annotationsToAdd)):

            # Add to local model
            self.local_model.append(annotationsToAdd[annotationIndex])

            # Add to general model
            self.model[type(annotationsToAdd[annotationIndex][0]).__name__].append(annotationsToAdd[annotationIndex])

            # Add them on the view
            self.addAnnotationItemOnView(annotationsToAdd[annotationIndex][1])

    # ───────────────
    # Private methods

    def _loadUserAnnotations(self, user_name):
        if not user_name in self.modelHandler.annotators:
            self.modelHandler.metadata[user_name] = dict()
            for supported_metadata_type in CheckCompatibility.getCompatibleMetadataTypes(self.modelHandler.type):
                self.modelHandler.metadata[user_name][str(supported_metadata_type)] = []

        DataController.model = self.modelHandler.metadata[user_name]
        self.local_model = []
        for supported_metadata_type in CheckCompatibility.getCompatibleMetadataTypes(self.modelHandler.type):
            self.local_model += self.model[str(supported_metadata_type)]

    def _showAnnotations(self):
        # Clear
        for existing_item in self.item_list:
            DataController.widget.main_widget.removeObject(existing_item)
        self.item_list = []
        # Display
        for annotationIndex in range(0,len(self.local_model)):
            self.addAnnotationItemOnView(self.local_model[annotationIndex][1])

    # ─────
    # Slots

    def onItemSelected(self, item):
        self.last_selected_item_index = self.item_list.index(item)
        self.last_selected_item_type = MetadataType[type(self.local_model[self.last_selected_item_index][0]).__name__]
        self.widget.displayObject(self.local_model[self.last_selected_item_index][0])

    def onItemCoordinatesChange(self, item, coordinates):
        # This will also affect the real model as it is a pointer
        self.local_model[self.item_list.index(item)][1] = coordinates

    def onTypeChangeRequest(self, message_type):
        # Retrieve the current type of the annotation
        old_message_type = self.last_selected_item_type

        # Remove annotation from its former category in model, and add it to the new one
        self.model[str(old_message_type)].remove(self.local_model[self.last_selected_item_index])
        self.model[str(message_type)].append(self.local_model[self.last_selected_item_index])

        # Then change the annotation type in the local_model (this will also be done in model because
        # it's a pointer)
        self.local_model[self.last_selected_item_index][0] = makeMetadataObject(message_type)

        # Register the current message type and send the selection signal as usual
        self.last_selected_item_type = message_type
        self.widget.displayObject(self.local_model[self.last_selected_item_index][0])

    def createNewItem(self, center_coordinates):
        x=center_coordinates[0]
        y=center_coordinates[1]

        # Create the new object as required
        new_object = [makeMetadataObject(self.last_selected_item_type),[[x-30,y-30],[x+30,y+30]]]

        # Add it to local and general model
        self.local_model.append(new_object)
        self.model[str(self.last_selected_item_type)].append(new_object)

        # Display it in the image widget
        r = self.addAnnotationItemOnView(self.local_model[-1][1])

        # Display information on it in data editor widget
        r.select()

    def deleteAnnotation(self, item):
        if self.widget.askForItemDeletion(item):
            self.last_selected_item_index = None
            index = self.item_list.index(item)
            self.item_list.remove(item)
            annotation = self.local_model.pop(index)
            self.model[type(annotation[0]).__name__].remove(annotation)

    def onUserChanged(self, user_name):
        self._loadUserAnnotations(user_name)
        self._showAnnotations()