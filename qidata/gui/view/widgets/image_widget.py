# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QSizePolicy, QGraphicsItem, QPen, QColor
from PySide.QtCore import Qt, QPoint

class ImageWidget(QGraphicsView):
	def __init__(self, imageItem):
		super(ImageWidget, self).__init__()

		# ─────────────
		# MODEL STORAGE

		self._model = imageItem
		# Here later we will load all rectangles stored in the model

		# ─────────────
		# VIEW CREATION

		# Create scene
		scene = QGraphicsScene()
		self.pixmapItem = scene.addPixmap(imageItem.pixmap)

		# Add scene to widget
		self.setScene(scene)

	# ──────
	# EVENTS

	def wheelEvent(self, event):
		focusedItem = self.scene().focusItem().rect()
		step = event.delta() / 120
		focusedItem.setTop(focusedItem.top()-5*step)
		focusedItem.setBottom(focusedItem.bottom()+5*step)
		focusedItem.setLeft(focusedItem.left()-5*step)
		focusedItem.setRight(focusedItem.right()+5*step)
		self.scene().focusItem().setRect(focusedItem)

	def mousePressEvent(self, event):
		position_scene = self.mapToScene(event.x(),event.y())
		position_widget = QPoint(event.x(), event.y())

		if not self.pixmapItem.contains(position_scene):
			# Click out of the zone
			# Maybe defocus ?
			return

		if len(self.items(position_widget)) == 1:
			# If no item is already there, create a new rectangle
			self.__addFocusedRect(position_scene.x()-30, position_scene.y()-30, position_scene.x()+30, position_scene.y()+30)

		else:
			# A rectangle exists, retrieve it
			selectedItem = self.items(position_widget)[0]

			focusedItem = self.scene().focusItem()
			if focusedItem is not None  and selectedItem == focusedItem:
				# If the selected rectangle is the focused one, just replace it
				rect = focusedItem.rect()
				rect.moveCenter(position_scene)
				focusedItem.setRect(rect)
			else:
				# If it is a different one, give him focus
				self.__setFocus(selectedItem)

	# ───────────────
	# PRIVATE METHODS

	def __addFocusedRect(self, x_min, y_min, x_max, y_max):
		r = self.__addRect(x_min, y_min, x_max, y_max)
		self.__setFocus(r)
		return r

	def __addRect(self, x_min, y_min, x_max, y_max):
		r = self.scene().addRect(x_min, y_min, x_max-x_min, y_max-y_min)
		r.setFlags(QGraphicsItem.ItemIsFocusable)
		r.setPen(QPen(QColor(0,0,0)))
		return r

	def __setFocus(self, r):
		r.setPen(QPen(QColor(255,255,255)))
		focusedItem = self.scene().focusItem()
		if focusedItem and focusedItem != r:
			focusedItem.setPen(QPen(QColor(0,0,0)))
		r.setFocus()

