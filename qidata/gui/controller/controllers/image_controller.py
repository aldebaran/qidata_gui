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

    # ───────────
    # Constructor

    def __init__(self, source_path):
        super(ImageController, self).__init__()
        DataController.modelHandler = makeDataItem(source_path)
        DataController.model = self.modelHandler.metadata
        DataController.widget = makeWidget(self.modelHandler)

        # Remember which item on the image widget was lastly selected
        self.last_selected_item = None

        # Remember which type was lastly required by user.
        # If none was required, use first annotation type
        self.last_selected_item_type = AnnotationTypes[0]

        # Store created items in same order as annotations in model
        self.item_list = []

        for annotationIndex in range(0,len(self.model)):
            self.addAnnotationItem(self.model[annotationIndex][1])

        self.widget.objectAdditionRequired.connect(self.createNewItem)

    # ───────────
    # Methods

    def addAnnotationItem(self, annotation_item):
        r = self.widget.addRect(annotation_item)
        r.isSelected.connect(lambda:self.onItemSelected(r))
        r.isMoved.connect(lambda x:self.onItemCoordinatesChange(r, x))
        r.isResized.connect(lambda x:self.onItemCoordinatesChange(r, x))
        self.item_list.append(r)
        return r

    # ─────
    # Slots

    def onItemSelected(self, item):
        self.last_selected_item = self.item_list.index(item)
        self.selectionChanged.emit(self.model[self.last_selected_item][0])

    def onItemCoordinatesChange(self, item, coordinates):
        self.model[self.item_list.index(item)][1] = coordinates

    def onTypeChangeRequest(self, message_type):
        self.model[self.last_selected_item][0] = makeAnnotationItems(message_type)
        self.last_selected_item_type = message_type
        self.selectionChanged.emit(self.model[self.last_selected_item][0])

    def createNewItem(self, center_coordinates):
        x=center_coordinates[0]
        y=center_coordinates[1]

        # Create the new object in the model as required
        new_object = [makeAnnotationItems(self.last_selected_item_type),[[x-30,y-30],[x+30,y+30]]]
        self.model.append(new_object)

        # Display it in the image widget
        r = self.addAnnotationItem(self.model[-1][1])

        # Display information on it in data editor widget
        r.select()