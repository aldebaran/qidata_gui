# -*- coding: utf-8 -*-

# Qt
from PySide.QtCore import Signal

# qidata
from ...models import makeDataItem
from ...view import makeWidget
from ..datacontroller import DataController
from qidata.annotationitems import *

class ImageController(DataController):

    # ───────
    # Signals

    selectionChanged = Signal((Person,), (Face,))
    clearAnnotation = Signal()

    # ───────────
    # Constructor

    def __init__(self, source_path):
        super(ImageController, self).__init__()
        DataController.modelHandler = makeDataItem(source_path)
        DataController.model = self.modelHandler.annotations
        self.local_model = self.model["Person"] + self.model["Face"]

        DataController.widget = makeWidget(self.modelHandler)

        # Remember which item on the image widget was lastly selected
        self.last_selected_item = None

        # Remember which type was lastly required by user.
        # If none was required, use first annotation type
        self.last_selected_item_type = AnnotationTypes[0]

        # Store created items in same order as annotations in local_model
        self.item_list = []

        for annotationIndex in range(0,len(self.local_model)):
            self.addAnnotationItem(self.local_model[annotationIndex][1])

        self.widget.objectAdditionRequired.connect(self.createNewItem)

    # ───────────
    # Methods

    def addAnnotationItem(self, annotation_item):
        r = self.widget.addRect(annotation_item)
        r.isSelected.connect(lambda:self.onItemSelected(r))
        r.isMoved.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.isResized.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.suppressionRequired.connect(lambda: self.deleteAnnotation(r))
        self.item_list.append(r)
        return r

    # ─────
    # Slots

    def onItemSelected(self, item):
        self.last_selected_item = self.item_list.index(item)
        self.selectionChanged.emit(self.local_model[self.last_selected_item][0])

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
        self.local_model[self.last_selected_item][0] = makeAnnotationItems(message_type)

        # Register the current message type and send the selection signal as usual
        self.last_selected_item_type = message_type
        self.selectionChanged.emit(self.local_model[self.last_selected_item][0])

    def createNewItem(self, center_coordinates):
        x=center_coordinates[0]
        y=center_coordinates[1]

        # Create the new object as required
        new_object = [makeAnnotationItems(self.last_selected_item_type),[[x-30,y-30],[x+30,y+30]]]

        # Add it to local and general model
        self.local_model.append(new_object)
        self.model[self.last_selected_item_type].append(new_object)

        # Display it in the image widget
        r = self.addAnnotationItem(self.local_model[-1][1])

        # Display information on it in data editor widget
        r.select()

    def deleteAnnotation(self, item):
        if self.widget.askForItemDeletion(item):
            self.last_selected_item = None
            index = self.item_list.index(item)
            self.item_list.remove(item)
            annotation = self.local_model.pop(index)
            self.model[type(annotation[0]).__name__].remove(annotation)
            self.clearAnnotation.emit()
