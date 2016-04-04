#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from PySide.QtGui import QWidget

class ImageWidget(QWidget):
	def __init__(self):
		super(ImageWidget, self).__init__()
		self.image = None

	def setImage(self, new_image):
		self.image = new_image
