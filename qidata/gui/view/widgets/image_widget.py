# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QGraphicsItem, QPen, QColor, QGraphicsRectItem, QGraphicsPixmapItem
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



class PixmapWidget(QGraphicsPixmapItem, QObject):

	# ───────
	# Signals

	isClicked = Signal(list)

	# ──────────
	# Contructor

	def __init__(self, image):
		QGraphicsPixmapItem.__init__(self, image)
		QObject.__init__(self)

	# ─────
	# Slots

	def mousePressEvent(self, event):
		self.isClicked.emit([event.scenePos().x(), event.scenePos().y()])



class ImageWidget(QGraphicsView, DataWidget):

	# ───────
	# Signals

	objectAdditionRequired = Signal(list)

	# ───────────
	# Constructor

	def __init__(self, imageItem):
		QGraphicsView.__init__(self)
		DataWidget.__init__(self)

		# Create scene
		scene = QGraphicsScene()

		# Create pixmap
		p = PixmapWidget(imageItem.data)

		# When pixmap is clicked, add a new box
		p.isClicked.connect(self.objectAdditionRequired)

		# Add pixmap to scene and scene to widget
		scene.addItem(p)
		self.setScene(scene)

	# ───────
	# Methods

	def addRect(self, coordinates, model_index):
		r = RectWidget(coordinates, model_index)
		r.setFlags(QGraphicsItem.ItemIsFocusable)
		self.scene().addItem(r)
		return r