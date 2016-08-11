# -*- coding: utf-8 -*-

# Qt
from PySide.QtGui import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QPixmap
from PySide.QtCore import Signal, QObject

# qidata
from ..metadata_items.rect_item import MetadataRectItem


class PixmapWidget(QGraphicsPixmapItem, QObject):

	# ───────
	# Signals

	isClicked = Signal(list)

	# ──────────
	# Contructor

	def __init__(self, pixmap, parent=None):
		"""
		PixmapWidget constructor

		:param pixmap: The image to display
		:param parent: This widget's parent
		"""
		QGraphicsPixmapItem.__init__(self, pixmap)
		QObject.__init__(self, parent)

	# ─────
	# Slots

	def mousePressEvent(self, event):
		self.isClicked.emit([event.scenePos().x(), event.scenePos().y()])



class ImageWidget(QGraphicsView):
	"""
    Widget specialized in displaying image with Metadata Objects
    """

	# ───────
	# Signals

	objectAdditionRequired = Signal(list)

	# ───────────
	# Constructor

	def __init__(self, image_raw_data, parent=None):
		"""
		ImageWidget constructor

		:param image_raw_data:  Image raw data
		:param parent:  Parent of this widget
		"""
		super(ImageWidget, self).__init__(parent)

		# Create scene
		scene = QGraphicsScene()

		# Create pixmap
		pix = QPixmap()
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