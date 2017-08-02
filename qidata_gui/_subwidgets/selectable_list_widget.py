# -*- coding: utf-8 -*-

# Third-party libraries
from PySide.QtGui import (QListWidget,
                          QListWidgetItem,
                          QAbstractItemView)
from PySide.QtCore import Signal


class SelectableListItem(QListWidgetItem):

	# ──────────
	# Contructor

	def __init__(self, name, value, parent=None):
		"""
		SelectableListItem constructor
		"""
		QListWidgetItem.__init__(self, name, view = parent)
		self.value = value


class SelectableListWidget(QListWidget):
	"""
	Widget to handle annotations that are not localized
	"""

	# ───────
	# Signals

	itemSelected = Signal(list)

	# ───────────
	# Constructor

	def __init__(self, parent=None):
		"""
		SelectableListWidget constructor

		:param parent: Parent of this widget
		:type parent: PySide.QtGui.QWidget
		"""
		super(SelectableListWidget, self).__init__(parent)
		self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
		self.itemClicked.connect(
		    lambda item: self.itemSelected.emit(item.value)
		)

	# ───────
	# Methods

	def addItem(self, name, value=None):
		"""
		Add an object to display on the view.

		:param name: The text to display on the item
		:type name: str
		:param value: The value represented by this item
		:return: Reference to the widget representing the object

		.. note::

		The returned reference is handy to connect callbacks on the
		widget signals. This reference is also needed to remove the object.
		"""
		return SelectableListItem(name, value if value else name, self)

	def removeItem(self, item):
		"""
		Remove item from the list

		:param item: Item to remove
		:type item: PySide.QtGui.QListWidgetItem
		"""
		self.takeItem(self.row(item))