# -*- coding: utf-8 -*-

# Standard Library
import os.path
import sys

# Qt
from PySide import QtGui
from PySide.QtGui import QApplication, QInputDialog, QMessageBox

# qidata
from qidata import qidatafile, qidataset

# qidata_gui
import qidata_gui
from qidata_gui.widgets import exceptions, QiDataSetWidget, QiDataWidget

# local
from .view import AnnotationMakerMainWindow

class AnnotationMakerApp(QApplication):
	"""
	Annotation application's main entry point.

	This tool follows the rule of the MVC organization.  ``AnnotationMakerApp``
	is the top level controller, contains a view (``AnnotationMakerMainWindow``).
	It has no model.

	Within the view is nested another MVC pattern. A new MVC "instance" is spawned
	each time a file is opened. The model is the file, the controller is the ``DataController``
	instance, and the view is a ``QiDataWidget`` instance.
	"""
	def __init__(self, path = None, current_item = None):
		QApplication.__init__(self, [])
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

		self.main_window = AnnotationMakerMainWindow(self.user_name, self.desktop_geometry)
		self.main_window.copyRequested.connect(self.copy)
		self.main_window.pasteRequested.connect(self.paste)


		# Controller for displayed data
		self.data_controller = None
		self._clipboard = None

		# ───────────────
		# Connect signals

		self.fs_explorer.path_selected.connect(self.setSelected)

		# ──────────
		# Initialize

		if path:      self.setRoot(path)
		if current_item: self.setSelected(current_item)

	# ──────────
	# Public API

	def run(self):
		self.main_window.show()
		try:
			self.exec_()
		except KeyboardInterrupt:
			pass

	def setRoot(self, new_root):
		self.fs_root = new_root
		self.fs_explorer.setRoot(new_root)

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

		# Create the controller for that path and display the corresponding qidata widget
		if qidatafile.isSupported(path) or qidataset.isDataset(path):
			try:
				if self.data_controller is not None:
					# There is already a controller, leave properly before switching
					self.data_controller.onExit(self.main_window.auto_save)
				self.data_controller = QiDataSetWidget(path, self.user_name) if qidataset.isDataset(path) else QiDataWidget(path, self.user_name)
				self.main_window.visualization_widget = self.data_controller
				self.main_window.visualization_widget.showMaximized()
				# self.main_window.copy_all_msg.setEnabled(True)
			except TypeError, e:
				print "TypeError:%s"%e
			except exceptions.UserCancelation:
				self.fs_explorer._cancelSelectionChange()
		elif os.path.isdir(path):
			answer = QtGui.QMessageBox.question(self.main_window,
			                                    "Not a data set yet",
			                                    "The folder you selected is not a QiDataSet yet. Do you want to turn it into one ?",
			                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
			if answer == QMessageBox.Yes:
				with qidataset.QiDataSet(path, "w"):
					pass
				self.setSelected(path)

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
	def fs_explorer(self):
		return self.main_window.fs_explorer

	@property
	def desktop_geometry(self):
		return self.desktop().availableGeometry()

	# ───────
	# Helpers

	def __setMetaInfo(self):
		self.setOrganizationName("Aldebaran")
		self.setOrganizationDomain("aldebaran.com")
		self.setApplicationName("qidata annotator")
		self.setApplicationVersion(qidata_gui.VERSION)


def main(args):
	qidata_app = AnnotationMakerApp(args[0])
	try:
		qidata_app.run()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	if len(sys.argv)>1:
		main(sys.argv[1:])
	else:
		main(["."])