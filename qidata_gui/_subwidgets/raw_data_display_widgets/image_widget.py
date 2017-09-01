# -*- coding: utf-8 -*-

# Standard libraries
import math
import os

# Third-party libraries
from PySide import QtGui, QtCore

# Local modules
from qidata_gui import RESOURCES_DIR
from image import Image, Colorspace
from .graphics_elements import AnnotationItem, Scene

class ImageROI(QtGui.QGraphicsRectItem, AnnotationItem):
	"""
	Item to show the position of an object on an image.
	"""

	# ──────────
	# Contructor

	def __init__(self, coordinates, info, parent=None):
		"""
		ImageROI constructor

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

class BackgroundPixmap(QtGui.QGraphicsPixmapItem):

	def __init__(self, image):
		pixmap = QtGui.QPixmap.fromImage(image)
		QtGui.QGraphicsPixmapItem.__init__(self, pixmap)

	# This is mandatory to send all events to the scene
	def mousePressEvent(self, event):
		event.ignore()

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
		self.scene.itemAdditionRequested.connect(
			    lambda x: self.itemAdditionRequested.emit(
			        self._locationToCoordinates(x)
			    )
			)
		self.scene.itemDeletionRequested.connect(self.itemDeletionRequested)
		self.scene.itemSelected.connect(self.itemSelected)
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

	def _locationToCoordinates(self, location):
		"""
		Create a proper set of coordinates to appropriately represent
		the given location on the data type.
		"""
		x=int(location.x())
		y=int(location.y())
		return [[x-30,y-30],[x+30,y+30]]
