
from PySide.QtGui import QTreeWidget

class EditableTree(QTreeWidget):
    def __init__(self, parent):
        super(EditableTree, self).__init__(parent)

