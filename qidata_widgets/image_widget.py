# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QGraphicsItem, QPen, QColor, QGraphicsRectItem, QGraphicsPixmapItem, QMessageBox, QPixmap
from PySide.QtCore import Signal, QObject, Qt
from .qidatawidget import QiDataWidget

class RectWidget(QGraphicsRectItem, QObject):

	# ───────
	# Signals

	isSelected = Signal()
	isMoved = Signal(list)
	isResized = Signal(list)
	suppressionRequired = Signal()

	# ──────────
	# Contructor

	def __init__(self, coordinates):
		x_min, y_min = coordinates[0]
		x_max, y_max = coordinates[1]
		QGraphicsRectItem.__init__(self, x_min, y_min, x_max-x_min, y_max-y_min)
		QObject.__init__(self)

	# ───────
	# Methods

	def select(self):
		self.setFocus()

	# ─────
	# Slots

	def focusInEvent(self, event):
		# Color in white
		self.setPen(QPen(QColor(255,255,255)))
		self.isSelected.emit()

	def focusOutEvent(self, event):
		# Color in black
		self.setPen(QPen(QColor(0,0,0)))

	def keyReleaseEvent(self, event):
		event.accept()

		# Resize the box depending on the hit key
		r = self.rect()
		if event.key() == Qt.Key_Up: # UP
			r.setTop(r.top()-5)
			r.setBottom(r.bottom()+5)
		elif event.key() == Qt.Key_Down: # DOWN
			r.setTop(r.top()+5)
			r.setBottom(r.bottom()-5)
		elif event.key() == Qt.Key_Right: # RIGHT
			r.setLeft(r.left()-5)
			r.setRight(r.right()+5)
		elif event.key() == Qt.Key_Left: # LEFT
			r.setLeft(r.left()+5)
			r.setRight(r.right()-5)
		elif event.key() == Qt.Key_Delete: # DEL
			self.suppressionRequired.emit()
			return

		self.setRect(r)

		# Emit new coordinates
		self.isResized.emit(
			[
				[r.left(), r.top()],
				[r.right(), r.bottom()]
			])

	def mouseMoveEvent(self, event):
		# Update box position in the scene
		p2 = event.scenePos()
		p1 = event.lastScenePos()
		dx = p2.x()-p1.x()
		dy = p2.y()-p1.y()
		r = self.rect()
		r.setTop(r.top() + dy)
		r.setBottom(r.bottom() + dy)
		r.setLeft(r.left() + dx)
		r.setRight(r.right() + dx)
		self.setRect(r)

	def mousePressEvent(self, event):
		# This give the focus to the item
		if event.button() == Qt.RightButton:
			self.suppressionRequired.emit()
		event.accept()

	def mouseReleaseEvent(self, event):
		# When mouse is released, emit coordinates in case it was moved
		r = self.rect()
		self.isMoved.emit(
			[
				[r.left(), r.top()],
				[r.right(), r.bottom()]
			])

	def wheelEvent(self, event):
		# Resize the box depending on wheel direction
		r = self.rect()
		step = event.delta() / 120
		r.setTop(r.top()-5*step)
		r.setBottom(r.bottom()+5*step)
		r.setLeft(r.left()-5*step)
		r.setRight(r.right()+5*step)
		self.setRect(r)

		# Emit new coordinates
		self.isResized.emit(
			[
				[r.left(), r.top()],
				[r.right(), r.bottom()]
			])



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



class ImageWidget(QGraphicsView, QiDataWidget):

	# ───────
	# Signals

	objectAdditionRequired = Signal(list)

	# ───────────
	# Constructor

	def __init__(self, imageItem):
		QGraphicsView.__init__(self)
		QiDataWidget.__init__(self)

		# Create scene
		scene = QGraphicsScene()

		# Create pixmap
		tmp_pix = QPixmap()
		tmp_pix.load(imageItem.datapath)
		p = PixmapWidget(tmp_pix)

		# When pixmap is clicked, add a new box
		p.isClicked.connect(self.objectAdditionRequired)

		# Add pixmap to scene and scene to widget
		scene.addItem(p)
		self.setScene(scene)

	# ───────
	# Methods

	def addRect(self, coordinates):
		r = RectWidget(coordinates)
		r.setFlags(QGraphicsItem.ItemIsFocusable)
		self.scene().addItem(r)
		return r

	def askForItemDeletion(self, item):
		response = QMessageBox.warning(self, "Suppression", "Are you sure you want to remove this annotation ?", QMessageBox.Yes | QMessageBox.No)
		if response == QMessageBox.Yes:
			self.scene().removeItem(item)
			return True
		return False

	def askForDataSave(self):
		response = QMessageBox.warning(self, "Leaving..", "You are about to leave this file. Do you want to save your modifications ?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
		return response