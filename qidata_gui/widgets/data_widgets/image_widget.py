# -*- coding: utf-8 -*-

# Qt
from PySide import QtGui, QtCore

# local
from ..metadata_items.rect_item import MetadataRectItem
from raw_data_widget import RawDataWidgetInterface

class PixmapWidget(QtGui.QGraphicsPixmapItem, QtCore.QObject):

	# ───────
	# Signals

	isClicked = QtCore.Signal(list)

	# ──────────
	# Contructor

	def __init__(self, pixmap, parent=None):
		"""
		PixmapWidget constructor

		:param pixmap: The image to display
		:param parent: This widget's parent
		"""
		QtGui.QGraphicsPixmapItem.__init__(self, pixmap)
		QtCore.QObject.__init__(self, parent)

	# ─────
	# Slots

	def mousePressEvent(self, event):
		self.isClicked.emit([event.scenePos().x(), event.scenePos().y()])

class ImageWidget(QtGui.QGraphicsView, RawDataWidgetInterface):
	"""
    Widget specialized in displaying image with Metadata Objects
    """

	# ───────────
	# Constructor

	def __init__(self, image_raw_data, parent=None):
		"""
		ImageWidget constructor

		:param image_raw_data:  Image raw data
		:param parent:  Parent of this widget
		"""
		QtGui.QGraphicsView.__init__(self, parent)

		# Create scene
		scene = QtGui.QGraphicsScene()

		# Create pixmap
		pix = QtGui.QPixmap()
		pix.loadFromData(image_raw_data)
		p = PixmapWidget(pix, self)

		# When pixmap is clicked, add a new box
		p.isClicked.connect(self.objectAdditionRequired)

		# Add pixmap to scene and scene to widget
		scene.addItem(p)
		self.setScene(scene)

	# ───────
	# Methods

	def addObject(self, coordinates):
		"""
		Add a metadata object to display on the view.

		:param coordinates:  Coordinates of the object to show (format depends on data type)
		:return:  Reference to the widget representing the object

		.. note::
			The returned reference is handy to connect callbacks on the
			widget signals. This reference is also needed to remove the object.
		"""
		r = MetadataRectItem(coordinates)
		self.scene().addItem(r)
		return r

	def removeItem(self, item):
		"""
		Remove an object from the widget

		:param item:  Reference to the widget
		"""
		self.scene().removeItem(item)

	def _locationToCoordinates(self, location):
		if location is not None:
			x=location[0]
			y=location[1]
			return [[x-30,y-30],[x+30,y+30]]
		else:
			return None