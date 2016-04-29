# -*- coding: utf-8 -*-

from PySide.QtCore import Qt
from PySide.QtGui import QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton, QSizePolicy

import math

class EditableTree(QTreeWidget):

    # ───────────
    # Constructor

    def __init__(self, parent):
        super(EditableTree, self).__init__(parent)

        # Take as much space as possible
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Two columns (key, value)
        self.setColumnCount(2)

        # Do not display column headers
        self.setHeaderHidden(True)

        # Resize the columns when some items are opened / close
        self.itemExpanded.connect(lambda: self.resizeColumnToContents(0))
        self.itemCollapsed.connect(lambda: self.resizeColumnToContents(0))
        self._message = None

    # ──────────
    # Properties

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, new_message):
        """
        Clears the tree view and displays the new message
        :param new_message: message object to display in the treeview
        """
        # Remember whether items were expanded or not before deleting
        if self._message:
            self.clear()
            self._message = None

        if new_message:
            self._message = new_message
            # Populate the tree
            self._refresh_msg_object()
        self.resizeColumnToContents(0)
        self.update()

    # ────────────────
    # Internal methods

    def _refresh_msg_object(self):
        self._display_sub_items(None, None, '', self._message)

    def _display_sub_items(self, parent_item, parent_obj, name, obj):
        pass

        value = None
        subobjs = []

        if hasattr(obj, '__dict__'):
            # obj is a class instance => retrieve its attributes to be displayed as sub-elements
            subobjs = obj.__dict__.items()

        elif type(obj) == dict:
            # obj is a container with keys  => retrieve its content to be displayed as sub-elements
            subobjs = obj.items()

        elif type(obj) in [list, tuple]:
            # obj is a container  without keys => retrieve its content to be displayed as sub-elements by numbers
            # Give those sub-elements a number as name (like "[42]")
            len_obj = len(obj)
            if len_obj != 0:
                w = int(math.ceil(math.log10(len_obj)))
                subobjs = [('[%*d]' % (w, i), subobj) for (i, subobj) in enumerate(obj)]
        else:
            # obj is a plain value  => display it
            if type(obj) == float:
                value = '%.6f' % obj
            elif type(obj) in [str, bool, int, long]:
                value = str(obj)
            else:
                print "Warning, unsupported type %s"%type(obj)

        ## Create item

        # First column
        item = QTreeWidgetItem([name, '']) # Set name in first column and leave the second one blank
        item.setData(0, Qt.UserRole, (parent_obj, type(obj))) # Store some info about displayed data

        if name == '':
            # Empty name means obj is the root => do nothing
            item = None
        elif parent_item is None:
            # This obj is a child of the root object
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        # Second column
        if item is not None:
            if value is not None:
                # obj is a value, display it in an editor widget
                inputWidget = QLineEdit(self)
                inputWidget.setText(value)
                # inputWidget.textChanged[str].connect(lambda x: self.onChanged(item, type(obj), x))
                self.setItemWidget(item, 1, inputWidget)

            elif type(obj) in [list, tuple]:
                # obj is a list, add a button to add elements
                inputWidget = QPushButton(self)
                inputWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                inputWidget.setText("Add element")
                # inputWidget.clicked.connect(lambda: self.elementAdditionRequired(item, parent_item, path, name, obj, obj_type))
                self.setItemWidget(item, 1, inputWidget)

        # Add sub-elements if any
        for subobj_name, subobj in subobjs:
            self._display_sub_items(item, obj, subobj_name, subobj)