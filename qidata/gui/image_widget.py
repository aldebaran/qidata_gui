#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from PySide.QtGui import QWidget

class ImageWidget(QWidget):
	def __init__(self):
		super(ImageWidget, self).__init__()
		self._image = None

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
