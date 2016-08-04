# -*- coding: utf-8 -*-

# Qt
from PySide.QtCore import Signal

# qidata
from qidata_file import qidatafile
from qidata_widgets import makeWidget
from ..datacontroller import DataController
from ...view import CentralWidget
from qidata_objects import *

class ImageController(DataController):

    # ───────────
    # Constructor

    def __init__(self, source_path):
        super(ImageController, self).__init__()
        DataController.modelHandler = qidatafile.open(source_path, "w")

        DataController.widget = CentralWidget(makeWidget("image", self.modelHandler))
        DataController.widget.annotation_selector_widget.user_selector_widget.addItems(self.modelHandler.annotators)
        self._loadUserAnnotations(DataController.widget.annotation_selector_widget.user_selector_widget.currentText())

        # Remember which item on the image widget was lastly selected
        self.last_selected_item = None

        # Remember which type was lastly required by user.
        # If none was required, use first annotation type
        self.last_selected_item_type = DataObjectTypes[0]

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
            if not type(annotationsToAdd[annotationIndex][0]).__name__ in ["Person", "Face"]:
                continue

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
            self.modelHandler.annotations[user_name] = dict(Face=[], Person=[])

        DataController.model = self.modelHandler.annotations[user_name]
        self.local_model = self.model["Person"] + self.model["Face"]

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
        self.last_selected_item = self.item_list.index(item)
        self.widget.displayObject(self.local_model[self.last_selected_item][0])

    def onItemCoordinatesChange(self, item, coordinates):
        # This will also affect the real model as it is a pointer
        self.local_model[self.item_list.index(item)][1] = coordinates

    def onTypeChangeRequest(self, message_type):
        # Retrieve the current type of the annotation
        old_message_type = type(self.local_model[self.last_selected_item][0]).__name__

        # Remove annotation from its former category in model, and add it to the new one
        self.model[old_message_type].remove(self.local_model[self.last_selected_item])
        self.model[message_type].append(self.local_model[self.last_selected_item])

        # Then change the annotation type in the local_model (this will also be done in model because
        # it's a pointer)
        self.local_model[self.last_selected_item][0] = makeDataObject(message_type)

        # Register the current message type and send the selection signal as usual
        self.last_selected_item_type = message_type
        self.widget.displayObject(self.local_model[self.last_selected_item][0])

    def createNewItem(self, center_coordinates):
        x=center_coordinates[0]
        y=center_coordinates[1]

        # Create the new object as required
        new_object = [makeDataObject(self.last_selected_item_type),[[x-30,y-30],[x+30,y+30]]]

        # Add it to local and general model
        self.local_model.append(new_object)
        self.model[self.last_selected_item_type].append(new_object)

        # Display it in the image widget
        r = self.addAnnotationItemOnView(self.local_model[-1][1])

        # Display information on it in data editor widget
        r.select()

    def deleteAnnotation(self, item):
        if self.widget.askForItemDeletion(item):
            self.last_selected_item = None
            index = self.item_list.index(item)
            self.item_list.remove(item)
            annotation = self.local_model.pop(index)
            self.model[type(annotation[0]).__name__].remove(annotation)

    def onUserChanged(self, user_name):
        self._loadUserAnnotations(user_name)
        self._showAnnotations()
        pass
