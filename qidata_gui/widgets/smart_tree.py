# -*- coding: utf-8 -*-

from PySide.QtCore import Qt
from PySide.QtGui import QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton, QSizePolicy

from qidata.metadata_objects import MetadataObjectBase, TypedList

import math

class SmartTreeWidget(QTreeWidget):
    """
    Tree widget displaying an object and giving the possibility to
    modify it.
    """

    # ───────────
    # Constructor

    def __init__(self, parent=None):
        """
        SmartTreeWidget constructor

        :param parent:  Parent of this widget
        """
        super(SmartTreeWidget, self).__init__(parent)

        # Take as much space as possible
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Three columns (key, value, delete button)
        self.setColumnCount(3)

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

        if isinstance(obj, MetadataObjectBase):
            # obj is a class instance => retrieve its attributes to be displayed as sub-elements
            subobjs = obj.__dict__.items()

        elif type(obj) == dict:
            # obj is a container with keys  => retrieve its content to be displayed as sub-elements
            subobjs = obj.items()

        elif type(obj) in [list, tuple, TypedList]:
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
            elif type(obj) in [str, bool, int, long, unicode]:
                value = str(obj)
            else:
                print "Warning, unsupported type %s"%type(obj)

        ## Create item

        # First column
        item = QTreeWidgetItem([name, '', '']) # Set name in first column and leave the second and third ones blank
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
                inputWidget.textChanged[str].connect(lambda x: self._onChanged(item, x))
                self.setItemWidget(item, 1, inputWidget)

            elif type(obj) in [TypedList]:
                # obj is a list, add a button to add elements
                inputWidget = QPushButton(self)
                inputWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                inputWidget.setText("Add element")
                inputWidget.clicked.connect(lambda: self._elementAdditionRequired(obj, item))
                self.setItemWidget(item, 1, inputWidget)

            elif type(obj) in [list, tuple]:
                # obj is a list without type, addition is not supported
                pass

        # Third column
        if name.startswith("[") and type(parent_obj) in [TypedList]:
            # This is an element of a custom list, that we might want to remove
            inputWidget = QPushButton(self)
            inputWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            inputWidget.setText("Remove element")
            inputWidget.clicked.connect(lambda: self._elementDeletionRequired(parent_obj, parent_item, item, name))
            self.setItemWidget(item, 2, inputWidget)

        # Add sub-elements if any
        for subobj_name, subobj in subobjs:
            self._display_sub_items(item, obj, subobj_name, subobj)

    def _onChanged(self, item, newvalue):
        parent_obj = item.data(0, Qt.UserRole)[0]
        obj_type = item.data(0, Qt.UserRole)[1]

        if item.text(0).startswith("["):
            index = int(item.text(0)[1:-1])
        else:
            index = item.text(0)

        if hasattr(parent_obj, '__dict__'):
            # obj is a class instance => retrieve its attributes to be displayed as sub-elements
            parent_obj.__setattr__(index, obj_type(newvalue))

        else:
            parent_obj[index] = obj_type(newvalue)

    def _elementAdditionRequired(self, obj, item):
        obj.appendDefault()
        len_obj = len(obj)
        w = int(math.ceil(math.log10(len_obj)))
        added_element_name = '[%*d]' % (w, len_obj-1)
        self._display_sub_items(item, obj, added_element_name, obj[-1])

    def _elementDeletionRequired(self, parent_obj, parent_item, item, name):
        # Retrieve the item index in the name
        index = int(name[1:-1])

        # parent_obj is the TypedList containing the element to remove
        parent_obj.pop(index)
        parent_item.removeChild(item)