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

        for annotationIndex in range(0,len(self.model)):
            r = self.widget.addRect(self.model[annotationIndex][1], annotationIndex)
            r.isSelected.connect(self.onItemSelected)
            r.isMoved.connect(self.onItemCoordinatesChange)
            r.isResized.connect(self.onItemCoordinatesChange)

        self.widget.objectAdditionRequired.connect(self.createNewItem)

    # ─────
    # Slots

    def onItemSelected(self, item_selected):
        self.last_selected_item = item_selected
        self.selectionChanged.emit(self.model[item_selected][0])

    def onItemCoordinatesChange(self, item_selected, coordinates):
        self.model[item_selected][1] = coordinates

    def onTypeChangeRequest(self, message_type):
        self.model[self.last_selected_item][0] = makeAnnotationItems(message_type)
        self.last_selected_item_type = message_type
        self.selectionChanged.emit(self.model[self.last_selected_item][0])

    def createNewItem(self, center_coordinates):
        x=center_coordinates[0]
        y=center_coordinates[1]

        # Create the new object in the model as required
        obj_index = len(self.model)
        new_object = [makeAnnotationItems(self.last_selected_item_type),[[x-30,y-30],[x+30,y+30]]]
        self.model.append(new_object)

        # Display it in the image widget
        r = self.widget.addRect(self.model[obj_index][1], obj_index)
        r.isSelected.connect(self.onItemSelected)
        r.isMoved.connect(self.onItemCoordinatesChange)
        r.isResized.connect(self.onItemCoordinatesChange)

        # Display information on it in data editor widget
        r.select()