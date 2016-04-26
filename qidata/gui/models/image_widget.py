# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsView, QGraphicsScene, QSizePolicy, QGraphicsItem, QPen, QColor
from PySide.QtCore import Qt, QPoint

class ImageWidget(QGraphicsView):
	def __init__(self, imageItem):
		super(ImageWidget, self).__init__()


		# Create scene
		scene = QGraphicsScene()
		self.pixmapItem = scene.addPixmap(imageItem.pixmap)

		# Add scene to widget
		self.setScene(scene)

	# ─────────────────
	# QWidget overrides

	def wheelEvent(self, event):
		print "WheelEvent", event

	def mousePressEvent(self, event):
		focusedItem = self.scene().focusItem()
		position_scene = self.mapToScene(event.x(),event.y())
		position_widget = QPoint(event.x(), event.y())
		x=position_scene.x()
		y=position_scene.y()

		if not self.pixmapItem.contains(position_scene):
			# Click out of the zone
			# Maybe defocus ?
			return

		if focusedItem is not None:
			# If an item is focused, show it in black (prepare focus lost)
			focusedItem.setPen(QPen(QColor(0,0,0)))

		if len(self.items(position_widget)) == 1:
			# If no item is already there, create a new rectangle
			rect = self.scene().addRect(position_scene.x()-30, position_scene.y()-30, 60,60)
			rect.setFlags(QGraphicsItem.ItemIsFocusable)
			rect.setPen(QPen(QColor(255,255,255)))
			# And give him focus
			rect.setFocus()

		else:
			# A rectangle exists, retrieve it
			selectedItem = self.items(position_widget)[0]

			if focusedItem is not None  and selectedItem == focusedItem:
				# If the selected rectangle is the focused one, just replace it
				rect = focusedItem.rect()
				rect.moveCenter(position_scene)
				focusedItem.setRect(rect)
			else:
				# If it is a different one, give him focus
				selectedItem.setFocus()

			# Show that this rectangle is the focused one.
			selectedItem.setPen(QPen(QColor(255,255,255)))


	# ──────────
	# Properties

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, new_image):
		self._image = new_image
