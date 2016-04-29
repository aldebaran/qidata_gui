# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QGraphicsItem, QPen, QColor, QGraphicsRectItem
from PySide.QtCore import QPoint, Signal, QObject
from ..datawidget import DataWidget

class RectWidget(QGraphicsRectItem, QObject):
	"""docstring for Rect"""

	isSelected = Signal(int)
	isMoved = Signal()

	def __init__(self, coordinates, model_index):
		x_min, y_min = coordinates[0]
		x_max, y_max = coordinates[1]
		QGraphicsRectItem.__init__(self, x_min, y_min, x_max-x_min, y_max-y_min)
		QObject.__init__(self)
		self.model_index = model_index

	def focusInEvent(self, event):
		self.setPen(QPen(QColor(255,255,255)))
		self.isSelected.emit(self.model_index)

	def focusOutEvent(self, event):
		self.setPen(QPen(QColor(0,0,0)))

	def wheelEvent(self, event):
		r = self.rect()
		step = event.delta() / 120
		r.setTop(r.top()-5*step)
		r.setBottom(r.bottom()+5*step)
		r.setLeft(r.left()-5*step)
		r.setRight(r.right()+5*step)
		self.setRect(r)

	# def mouseDoubleClickEvent(self, event):
	# 	position_scene = self.mapToScene(event.x(),event.y())
	# 	position_widget = QPoint(event.x(), event.y())

	# 	if len(self.items(position_widget)) == 1:
	# 		# If no item is already there, create a new rectangle
			# selectedItem = self.__addFocusedRect([[position_scene.x()-30, position_scene.y()-30], [position_scene.x()+30, position_scene.y()+30]])
	# 		# self.objectSelected.emit(selectedItem)

	# 	else:
	# 		# A rectangle exists, retrieve it
	# 		selectedItem = self.items(position_widget)[0]

	# 		focusedItem = self.scene().focusItem()
	# 		if focusedItem is not None  and selectedItem == focusedItem:
	# 			# If the selected rectangle is the focused one, just replace it
	# 			rect = focusedItem.rect()
	# 			rect.moveCenter(position_scene)
	# 			focusedItem.setRect(rect)

class ImageWidget(QGraphicsView, DataWidget):

	# ───────────
	# CONSTRUCTOR

	def __init__(self, imageItem):
		QGraphicsView.__init__(self)
		DataWidget.__init__(self)

		# Create scene
		scene = QGraphicsScene()
		self.pixmapItem = scene.addPixmap(imageItem.data)

		# Add scene to widget
		self.setScene(scene)

		# Add a rectangle for each element
		# This depends on dataItem API (ie dataItem version)
		# Keep a reference to the data through the visual items
		# self.__linkViewModel = dict()
		# for person in imageItem.metadata["persons"]:
		# 	r = self.__addRect(person[1])
		# 	self.__linkViewModel[r] = person[0]

		# for face in imageItem.metadata["faces"]:
		# 	self.__addRect(face[1])
		# 	self.__linkViewModel[r] = face[0]

	# ───────
	# SIGNALS

	objectSelected = Signal(list())
	objectPositionUpdated = Signal(list())

	# ─────
	# SLOTS

	# def mousePressEvent(self, event):
	# 	position_scene = self.mapToScene(event.x(),event.y())
	# 	position_widget = QPoint(event.x(), event.y())

	# 	if len(self.items(position_widget)) == 1:
	# 		# If no item is already there, create a new rectangle
			# selectedItem = self.__addFocusedRect([[position_scene.x()-30, position_scene.y()-30], [position_scene.x()+30, position_scene.y()+30]])
	# 		# self.objectSelected.emit(selectedItem)

	# 	else:
	# 		# A rectangle exists, retrieve it
	# 		selectedItem = self.items(position_widget)[0]

	# 		focusedItem = self.scene().focusItem()
	# 		if focusedItem is not None  and selectedItem == focusedItem:
	# 			# If the selected rectangle is the focused one, just replace it
	# 			rect = focusedItem.rect()
	# 			rect.moveCenter(position_scene)
	# 			focusedItem.setRect(rect)
	# 			# self.objectPositionUpdated.emit(selectedItem)
	# 		else:
	# 			# If it is a different one, give him focus
	# 			self.__setFocus(selectedItem)
	# 			# self.objectSelected.emit(selectedItem)

	# ───────────────
	# PRIVATE METHODS

	def addRect(self, coordinates, model_index):
		"""
		"""
		r = RectWidget(coordinates, model_index)
		r.setFlags(QGraphicsItem.ItemIsFocusable)
		self.scene().addItem(r)
		return r