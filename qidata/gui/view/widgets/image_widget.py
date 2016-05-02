# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QGraphicsItem, QPen, QColor, QGraphicsRectItem, QGraphicsPixmapItem
from PySide.QtCore import QPoint, Signal, QObject
from ..datawidget import DataWidget

class RectWidget(QGraphicsRectItem, QObject):

	# ───────
	# Signals

	isSelected = Signal(int)
	isMoved = Signal(int, list)
	# ──────────
	# Contructor

	def __init__(self, coordinates, model_index):
		x_min, y_min = coordinates[0]
		x_max, y_max = coordinates[1]
		QGraphicsRectItem.__init__(self, x_min, y_min, x_max-x_min, y_max-y_min)
		QObject.__init__(self)
		self.model_index = model_index

	# ───────
	# Methods

	def select(self):
		self.setFocus()

	# ─────
	# Slots

	def focusInEvent(self, event):
		self.setPen(QPen(QColor(255,255,255)))
		self.isSelected.emit(self.model_index)

	def focusOutEvent(self, event):
		self.setPen(QPen(QColor(0,0,0)))

	def mouseMoveEvent(self, event):
		p2 = event.scenePos()
		p1 = event.lastScenePos()
		self.moveBy(p2.x()-p1.x(), p2.y()-p1.y())

	def mousePressEvent(self, event):
		# This give the focus to the item
		event.accept()

	def mouseReleaseEvent(self, event):
		# When mouse is released, update the position in case it was moved
		self.isMoved.emit(self.model_index, [[self.pos().x(), self.pos().y()], [self.pos().x()+self.rect().width(), self.pos().y()+self.rect().height()]])

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