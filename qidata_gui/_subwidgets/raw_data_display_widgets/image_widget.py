# -*- coding: utf-8 -*-

# Standard libraries
import os

# Third-party libraries
from PySide import QtGui, QtCore
import numpy

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

	# ─────
	# Slots

	# Automatically called by Qt when a user clicks on the item
	def focusInEvent(self, event):
		self.parent.selectItem(self)

class ImageWidget(QtGui.QWidget):
	"""
	Widget specialized in displaying image with Metadata Objects
	"""

	itemSelected = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, image_raw_data, parent=None):
		"""
		ImageWidget constructor

		:param image_raw_data:  Image raw data
		:param parent:  Parent of this widget
		"""
		QtGui.QWidget.__init__(self, parent)

		self._selected = None #: Currently selected item

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
		self.fit_button.setText("");
		self.fit_button.setToolTip("Resize image so that it fits the window");
		self.fit_button.setIcon(fit_ic);
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
		self.full_button.setText("");
		self.full_button.setToolTip("Display image at its original size");
		self.full_button.setIcon(act_ic);
		self.full_button.setIconSize(act_ic.availableSizes()[0])
		self.full_button.clicked.connect(self._fullView)

		# Aggregation
		self.top_layout = QtGui.QHBoxLayout(self)
		self.top_layout.addWidget(self.fit_button)
		self.top_layout.addWidget(self.full_button)
		self.top_widget.setLayout(self.top_layout)

		## Center Graphic scene
		self.view = QtGui.QGraphicsView(self)
		self.view.setScene(QtGui.QGraphicsScene())

		# Add pixmap to scene and scene to widget
		self._pixmap = self.view.scene().addPixmap(
		                   QtGui.QPixmap.fromImage(
		                   	   Image(image_raw_data).qimage
		                   )
		               )

		## Aggregation
		self.main_layout = QtGui.QVBoxLayout(self)
		self.main_layout.addWidget(self.top_widget)
		self.main_layout.addWidget(self.view)
		self.setLayout(self.main_layout)


	# ──────────
	# Public API

	def addItem(self, location, info):
		r = ImageROI(location, info, self)
		self.view.scene().addItem(r)
		return r

	def selectItem(self, item):
		if item is self._selected:
			return
		self.focusOutSelectedItem()
		self._selected = item
		item.select()
		self.itemSelected.emit(item.info)

	def focusOutSelectedItem(self):
		if self._selected is not None:
			self._selected.deselect()
			self._selected = None

	def clearAllItems(self):
		item_list = self.view.scene().items()
		for item_index in range(len(item_list)-1):
			self.view.scene().removeItem(item_list[item_index])

	# ───────────
	# Private API

	def _fitContentToWindow(self):
		self.view.fitInView(self.view.scene().sceneRect(),
			                QtCore.Qt.KeepAspectRatio)

	def _fullView(self):
		view_rect = self.view.viewport().geometry()
		visible_scene_rect = self.view.mapToScene(view_rect).boundingRect()
		self.view.scale(
		    visible_scene_rect.width()/view_rect.width(),
		    visible_scene_rect.height()/view_rect.height()
		)
