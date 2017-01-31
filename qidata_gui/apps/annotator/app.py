# -*- coding: utf-8 -*-

# Standard Library
import os.path
import sys

# Qt
from PySide.QtCore import Signal, Slot
from PySide.QtGui import QApplication, QInputDialog

# qidata
from qidata import qidatafile, qidataset

# local
import qidata_gui
from .view import QiDataMainWindow
from .controller.datacontroller import SelectionChangeCanceledByUser
from .controller import controllerfactory

class QiDataApp(QApplication):
	def __init__(self, path = None, current_item = None):
		super(QiDataApp, self).__init__([])
		self.__setMetaInfo()

		self.fs_root         = path
		self.current_dataset = None
		self.current_item    = current_item
		self.user_name       = ""

		while str(self.user_name) == "":
			user_setting = QInputDialog.getText(None, "User ID", "Enter your ID (e.g. \"jdoe\")")
			if user_setting[1]:
				self.user_name = user_setting[0]

		# ───
		# GUI

		self.main_window = QiDataMainWindow(self.user_name, self.desktop_geometry)
		self.main_window.copyRequested.connect(self.copy)
		self.main_window.pasteRequested.connect(self.paste)


		# Controller for displayed data
		self.data_controller = None
		self._clipboard = None

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
		while not qidataset.isDataset(candidate_dataset):
			if self.fs_root and os.path.samefile(candidate_dataset, self.fs_root):
				break
			candidate_dataset = os.path.dirname(candidate_dataset)

			# print os.path.dirname(path)
			# if data.isDataset(path):
			# 	pass

		# ───────────
		# ?

		if qidatafile.isSupported(path):
			# Show the item in an visualization widget
			try:
				if self.data_controller is not None:
					# There is already a controller, leave properly before switching
					self.data_controller.onExit(self.main_window.auto_save)
				self.data_controller = controllerfactory.makeDataController(path, self.user_name)
				self.main_window.visualization_widget = self.data_controller.widget
				self.main_window.visualization_widget.showMaximized()
				self.main_window.copy_all_msg.setEnabled(True)
			except TypeError, e:
				print "TypeError:%s"%e
			except SelectionChangeCanceledByUser:
				self.data_explorer._cancelSelectionChange()

	def copy(self):
		if self.data_controller is not None:
			self._clipboard = self.data_controller.local_model
			self.main_window.paste_all_msg.setEnabled(True)

	def paste(self):
		if self.data_controller is not None and self._clipboard is not None:
			self.data_controller.addAnnotationItems(self._clipboard)
		pass

	# ──────────
	# Properties

	@property
	def data_explorer(self):
		return self.main_window.data_explorer

	@property
	def dataitem_editor(self):
		return self.main_window.message_creation

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
		self.setApplicationName("qidata annotator")
		self.setApplicationVersion(qidata_gui.VERSION)
