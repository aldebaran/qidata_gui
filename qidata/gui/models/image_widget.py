# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QBrush
from PySide.QtCore import Qt

class ImageWidget(QGraphicsView):
	def __init__(self, imageItem):
		super(ImageWidget, self).__init__()

		# Create brush
		# brush = QBrush(imageItem.pixmap)
		# brush.setStyle(Qt.SolidPattern)

		# Create scene
		scene = QGraphicsScene()
		# scene.setBackgroundBrush(brush)
		scene.addPixmap(imageItem.pixmap)

		# Add scene to widget
		self.setScene(scene)

	# ─────────────────
	# QWidget overrides

	def wheelEvent(self, event):
		print "WheelEvent", event

	def mousePressEvent(self, event):
		print "MousePressEvent", event

	# ──────────
	# Properties

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, new_image):
		self._image = new_image
