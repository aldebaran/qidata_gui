#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import sys
# Qt
from PySide.QtCore import Signal, Slot
from PySide.QtGui import QApplication
# qidata
import qidata
from .window import QiDataMainWindow

class QiDataApp(QApplication):
	def __init__(self, root = None, selected = None):
		super(QiDataApp, self).__init__([])
		self.__setMetaInfo()

		self.root     = root
		self.selected = selected

		# ───
		# GUI

		self.main_window = QiDataMainWindow(self.desktop_geometry)

		# ───────────────
		# Connect signals

		self.data_explorer.path_selected.connect(self.setSelected)

		# ──────────
		# Initialize

		if root:     self.setRoot(root)
		if selected: self.setSelected(selected)

	# ────────
	# Main API

	def setRoot(self, new_root):
		self.root = new_root
		self.data_explorer.setRoot(new_root)

	def setSelected(self, path):
		# Lookup the type of data
		# Load the data in a model of it
		# Instanciate an appropriate widget for it
		print "Selected data:", path

	# ──────────
	# Properties

	@property
	def data_explorer(self):
		return self.main_window.data_explorer

	@property
	def desktop_geometry(self):
		return self.desktop().availableGeometry()

	# ────────
	# Main API

	def run(self):
		self.main_window.show()
		self.exec_()

	# ───────
	# Helpers

	def __setMetaInfo(self):
		self.setOrganizationName("Aldebaran")
		self.setOrganizationDomain("aldebaran.com")
		self.setApplicationName("qidata")
		self.setApplicationVersion(qidata.VERSION)
