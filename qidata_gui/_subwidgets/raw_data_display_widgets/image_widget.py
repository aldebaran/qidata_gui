# -*- coding: utf-8 -*-

# Standard libraries
import math
import os

# Third-party libraries
from PySide import QtGui, QtCore

# Local modules
from qidata_gui import RESOURCES_DIR
from .image import Image, Colorspace

class ImageROI(QtGui.QGraphicsRectItem):
	"""
	Item to show the position of an object on an image.
	"""

	# ──────────
	# Contructor

	def __init__(self, coordinates, info, parent=None):
		"""
		QiDataObjectRectItem constructor

		:param coordinates: Object position
		:type coordinates: list
		:param info: Data represented by this item
		:param parent: Parent of this widget
		:type parent: QtGui.QWidget
		"""
		x_min, y_min = coordinates[0]
		x_max, y_max = coordinates[1]
		QtGui.QGraphicsRectItem.__init__(self,
		                             x_min,
		                             y_min,
		                             x_max-x_min,
		                             y_max-y_min)
		self.setFlags(QtGui.QGraphicsItem.ItemIsFocusable)
		self.setPen(QtGui.QPen(QtGui.QColor(255,0,0)))
		self.info = info
		self.coordinates = coordinates
		self.parent = parent

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

	def move(self, d):
		"""
		Move this item

		:param d: Translation to apply
		:type d: QtGui.QPoint
		"""
		dx = int(math.floor(0.5+d.x()))
		dy = int(math.floor(0.5+d.y()))
		self.moveBy(dx,dy)
		self.coordinates[0][0] = self.coordinates[0][0] + dx
		self.coordinates[0][1] = self.coordinates[0][1] + dy
		self.coordinates[1][0] = self.coordinates[1][0] + dx
		self.coordinates[1][1] = self.coordinates[1][1] + dy

	def increaseSize(self, horizontal, vertical):
		r = self.rect()
		r.setTop(r.top()-vertical)
		r.setBottom(r.bottom()+vertical)
		r.setLeft(r.left()-horizontal)
		r.setRight(r.right()+horizontal)
		self.coordinates[0][0] = self.coordinates[0][0] - horizontal
		self.coordinates[0][1] = self.coordinates[0][1] - vertical
		self.coordinates[1][0] = self.coordinates[1][0] + horizontal
		self.coordinates[1][1] = self.coordinates[1][1] + vertical
		self.setRect(r)

	# ─────
	# Slots

	# This is mandatory to send all events to the scene
	def mousePressEvent(self, event):
		event.ignore()

class BackgroundPixmap(QtGui.QGraphicsPixmapItem):

	def __init__(self, image):
		pixmap = QtGui.QPixmap.fromImage(image)
		QtGui.QGraphicsPixmapItem.__init__(self, pixmap)

	# This is mandatory to send all events to the scene
	def mousePressEvent(self, event):
		event.ignore()

class Scene(QtGui.QGraphicsScene):

	# ──────────
	# Contructor

	def __init__(self, parent_view):
		QtGui.QGraphicsScene.__init__(self)
		self._selectedItem = None
		self._parent_view = parent_view

	# ──────────
	# Public API

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
		self._parent_view.itemSelected.emit(item.info)

	def focusOutSelectedItem(self):
		if self._selectedItem is not None:
			self._selectedItem.deselect()
			self._selectedItem = None

	def clearAllItems(self):
		self.focusOutSelectedItem()
		item_list = self.items()
		for item_index in range(len(item_list)-1):
			self.removeItem(item_list[item_index])

	# ─────
	# Slots

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
					self._parent_view.itemDeletionRequested.emit(
					    self._selectedItem
					)

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
		if len(clicked_items)>0\
		   and isinstance(clicked_items[-1], QtGui.QGraphicsPixmapItem):
			clicked_items.pop(-1)

		if len(clicked_items)==0\
		   and not self._parent_view.read_only\
		   and event.button() == QtCore.Qt.LeftButton:
			self._parent_view.itemAdditionRequested.emit(
			                                             [
			                                              event.scenePos().x(),
			                                              event.scenePos().y()
			                                             ]
			                                            )

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
			self._parent_view.itemDeletionRequested.emit(self._selectedItem)

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

class ImageWidget(QtGui.QWidget):
	"""
	Widget specialized in displaying image with Metadata Objects
	"""

	itemAdditionRequested = QtCore.Signal(list)
	itemDeletionRequested = QtCore.Signal(list)
	itemSelected = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, image_raw_data, parent=None):
		"""
		ImageWidget constructor

		:param image_raw_data: Image raw data
		:param parent: Parent of this widget
		:type parent: PySide.QtGui.QWidget
		"""
		QtGui.QWidget.__init__(self, parent)

		self._selectedItem = None #: Currently selected item

		### Create GUI

		## Header
		self.top_widget = QtGui.QWidget(self)

		# "Fit window" button
		self.fit_button = QtGui.QPushButton("", self.top_widget)
		fit_ic_path = os.path.join(RESOURCES_DIR, "zoom_fit.png")
		fit_ic = QtGui.QIcon(fit_ic_path)
		self.fit_button.setFixedSize(
		    fit_ic.actualSize(
		        fit_ic.availableSizes()[0]
		    )
		)
		self.fit_button.setText("")
		self.fit_button.setToolTip("Resize image so that it fits the window")
		self.fit_button.setIcon(fit_ic)
		self.fit_button.setIconSize(fit_ic.availableSizes()[0])
		self.fit_button.clicked.connect(self._fitContentToWindow)

		# "Full size" button
		self.full_button = QtGui.QPushButton("", self.top_widget)
		actual_ic_path = os.path.join(RESOURCES_DIR, "zoom_actual.png")
		act_ic = QtGui.QIcon(actual_ic_path)
		self.full_button.setFixedSize(
		    act_ic.actualSize(
		        act_ic.availableSizes()[0]
		    )
		)
		self.full_button.setText("")
		self.full_button.setToolTip("Display image at its original size")
		self.full_button.setIcon(act_ic)
		self.full_button.setIconSize(act_ic.availableSizes()[0])
		self.full_button.clicked.connect(self._fullView)

		# Aggregation
		self.top_layout = QtGui.QHBoxLayout(self)
		self.top_layout.addWidget(self.fit_button)
		self.top_layout.addWidget(self.full_button)
		self.top_widget.setLayout(self.top_layout)

		## Center Graphic scene
		self.view = QtGui.QGraphicsView(self)
		self.scene = Scene(self)
		self.view.setScene(self.scene)

		# Add pixmap to scene and scene to widget
		self._pixmap = self.scene.addItem(
		                   BackgroundPixmap(
		                   	   Image(image_raw_data).qimage
		                   )
		               )

		## Aggregation
		self.main_layout = QtGui.QVBoxLayout(self)
		self.main_layout.addWidget(self.top_widget)
		self.main_layout.addWidget(self.view)
		self.setLayout(self.main_layout)

		# By default, the widget does not allow any modifications
		self.read_only = True


	# ──────────
	# Properties

	@property
	def read_only(self):
		return self._read_only

	@read_only.setter
	def read_only(self, new_value):
		self._read_only = new_value

	# ──────────
	# Public API

	def addItem(self, location, info):
		r = ImageROI(location, info, self)
		self.scene.addItem(r)
		return r

	def removeItem(self, item):
		self.scene.removeItem(item)

	def selectItem(self, item):
		self.scene.selectItem(item)

	def focusOutSelectedItem(self):
		self.scene.focusOutSelectedItem()

	def clearAllItems(self):
		self.scene.clearAllItems()

	# ───────────
	# Private API

	def _fitContentToWindow(self):
		self.view.fitInView(self.scene.sceneRect(),
			                QtCore.Qt.KeepAspectRatio)

	def _fullView(self):
		view_rect = self.view.viewport().geometry()
		visible_scene_rect = self.view.mapToScene(view_rect).boundingRect()
		self.view.scale(
		    visible_scene_rect.width()/view_rect.width(),
		    visible_scene_rect.height()/view_rect.height()
		)
