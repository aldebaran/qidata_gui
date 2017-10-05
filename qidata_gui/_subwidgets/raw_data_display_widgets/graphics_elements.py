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

# Standard libraries
import os

# Third-party libraries
from PySide import QtGui, QtCore

class AnnotationItem(object):

	# ──────────
	# Public API

	def select(self):
		"""
		Selects this specific item.
		"""
		pen = QtGui.QPen(QtGui.QColor(255,255,255)) # Color in white
		pen.setWidth(3) # Increase rectangle width
		self.setPen(pen) # Apply changes

	def deselect(self):
		"""
		Deselects this specific item.
		"""
		self.setPen(QtGui.QPen(QtGui.QColor(255,0,0))) # Color in red
		self.clearFocus()

	# ─────
	# Slots

	# This is mandatory to send all events to the scene
	def mousePressEvent(self, event):
		event.ignore()

class Scene(QtGui.QGraphicsScene):

	itemAdditionRequested = QtCore.Signal(list)
	itemDeletionRequested = QtCore.Signal(list)
	itemSelected = QtCore.Signal(list)

	# ──────────
	# Contructor

	def __init__(self, parent_view):
		QtGui.QGraphicsScene.__init__(self)
		self._selectedItem = None
		self._parent_view = parent_view
		self.setBackgroundBrush(QtCore.Qt.lightGray)

	# ──────────
	# Public API

	def items(self, pos=None):
		if pos is None:
			items = super(Scene, self).items()
		else:
			items = super(Scene, self).items(pos)

		i=len(items)-1
		while i > -1:
			if not isinstance(items[i], AnnotationItem):
				items.pop(i)
			i -= 1

		return items

	def refreshItems(self):
		for item in self.items():
			item._refresh()

	def removeItem(self, item):
		if item is self._selectedItem:
			self.focusOutSelectedItem()
		super(Scene, self).removeItem(item)

	def selectItem(self, item):
		if item is self._selectedItem:
			return
		self.focusOutSelectedItem()
		self._selectedItem = item
		item.select()
		self.itemSelected.emit(item.info)

	def focusOutSelectedItem(self):
		if self._selectedItem is not None:
			self._selectedItem.deselect()
			self._selectedItem = None

	def clearAllItems(self):
		self.focusOutSelectedItem()
		item_list = self.items()
		for item in item_list:
			self.removeItem(item)

	# ─────
	# Slots

	def mousePressEvent(self, event):
		event.accept()

	def keyPressEvent(self, event):
		event.accept()
		if self._parent_view.read_only:
			return

		if self._selectedItem is not None:
			if event.key() == QtCore.Qt.Key_Up: # UP
				self._selectedItem.increaseSize(0, 5)
			elif event.key() == QtCore.Qt.Key_Down: # DOWN
				self._selectedItem.increaseSize(0, -5)
			elif event.key() == QtCore.Qt.Key_Right: # RIGHT
				self._selectedItem.increaseSize(5, 0)
			elif event.key() == QtCore.Qt.Key_Left: # LEFT
				self._selectedItem.increaseSize(-5, 0)
			elif event.key() == QtCore.Qt.Key_Delete: # DEL
				if not self._parent_view.read_only\
				   and self._selectedItem is not None:
					self.itemDeletionRequested.emit(self._selectedItem)

	def mouseMoveEvent(self, event):
		event.accept()
		if self._parent_view.read_only:
			return
		clicked_items = self.items(event.lastScenePos())
		if self._selectedItem in clicked_items:
			self._selectedItem.move(event.scenePos() - event.lastScenePos())

	def mouseReleaseEvent(self, event):
		event.accept()

		# Retrieve all items concerned by the click except the base pixmap
		clicked_items = self.items(event.scenePos())

		if len(clicked_items)==0\
		   and not self._parent_view.read_only\
		   and event.button() == QtCore.Qt.LeftButton:
			self.itemAdditionRequested.emit(event.scenePos())

		elif len(clicked_items)>0 and event.button() == QtCore.Qt.LeftButton:
			i = len(clicked_items)-1
			while i>-1:
				if clicked_items[i] == self._selectedItem:
					break
				i=i-1
			self.selectItem(clicked_items[(i+1)%len(clicked_items)])
		elif len(clicked_items)>0\
		     and event.button() == QtCore.Qt.RightButton\
		     and not self._parent_view.read_only\
		     and self._selectedItem in clicked_items:
			self.itemDeletionRequested.emit(self._selectedItem)

	def wheelEvent(self, event):
		event.accept()
		# Resize the box depending on wheel direction
		if self._parent_view.read_only:
			return
		if self._selectedItem is not None:
			# delta encodes the angle rotated in a certain amount of units.
			# 120 units represents 15 degrees, which is a classical basic step
			# on most mice.
			# Here we decided arbitrarily that a 5 degree rotation (40 units)
			# would increase the size of an item by 1 pixel (on each side).
			# This means a classical mouse step will increase the size of an
			# item by 3 pixels on each side, leading to a global 6-pixel increase
			# on width and height. Finer mice might have a smaller resolution
			# but cannot go under 2-pixel increase on height and width
			r = self._selectedItem.rect()
			increase = event.delta() / 40
			self._selectedItem.increaseSize(increase, increase)
