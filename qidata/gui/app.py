# -*- coding: utf-8 -*-

# Standard Library
import os.path
import sys
# Qt
from PySide.QtCore import Signal, Slot
from PySide.QtGui import QApplication
# qidata
import qidata
from .models import data
from .view import makeWidget, QiDataMainWindow

class QiDataApp(QApplication):
	def __init__(self, path = None, current_item = None):
		super(QiDataApp, self).__init__([])
		self.__setMetaInfo()

		self.fs_root         = path
		self.current_dataset = None
		self.current_item    = current_item

		# ───
		# GUI

		self.main_window = QiDataMainWindow(self.desktop_geometry)

		# ───────────────
		# Connect signals

		self.data_explorer.path_selected.connect(self.setSelected)

		# ──────────
		# Initialize

		if path:      self.setRoot(path)
		if current_item: self.setSelected(current_item)

	# ────────
	# Main API

	def setRoot(self, new_root):
		self.fs_root = new_root
		self.data_explorer.setRoot(new_root)

	def setSelected(self, path):
		# ───────────────────────────
		# Find the containing dataset

		containing_dataset = None

		candidate_dataset = path
		while not data.isDataset(candidate_dataset):
			if self.fs_root and os.path.samefile(candidate_dataset, self.fs_root):
				break
			candidate_dataset = os.path.dirname(candidate_dataset)

			# print os.path.dirname(path)
			# if data.isDataset(path):
			# 	pass

		# ───────────
		# ?

		if data.isSupportedItem(path):
			# Show the item in an visualization widget
			try:
				dataItem = data.makeDataItem(path)
				self.main_window.visualization_widget = makeWidget(dataItem)
				self.main_window.visualization_widget.showMaximized()
			except TypeError, e:
				print e

		# Lookup the type of data
		# Load the data in a model of it
		# Instanciate an appropriate widget for it

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
