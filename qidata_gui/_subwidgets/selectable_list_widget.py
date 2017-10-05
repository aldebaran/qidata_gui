# -*- coding: utf-8 -*-

# Copyright (c) 2017, Softbank Robotics Europe
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

		# Emit newly selected item info
		# If new item is None, emit nothing (it happens when item is set to
		# None to deselect all)
		self.currentItemChanged.connect(
		    lambda current, previous:
		        None if current is None\
		        else self.itemSelected.emit(current.value)
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

	def deselectAll(self):
		"""
		De-focus any focused item
		"""
		self.setCurrentItem(None)

	def removeSelectedItem(self):
		"""
		Removes the item which is selected. Does not do anything if no item is
		selected
		"""
		row_to_remove = self.currentRow()
		self.deselectAll()
		if row_to_remove != -1:
			self.takeItem(row_to_remove)

	def clearAllItems(self):
		"""
		Remove all items from the list
		"""
		self.clear()
