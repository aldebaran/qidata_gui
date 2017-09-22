# -*- coding: utf-8 -*-

# Standard libraries
import argparse
import os
import sys

# Third-party libraries
from PySide import QtCore, QtGui
import qidata

# Local modules
from qidata_apps import QiDataApp
from qidata_gui import QiDataSensorWidget, QiDataSetWidget
from .file_system_explorer import FileSystemExplorer

class App(QiDataApp):

	# ───────────
	# Constructor

	def __init__(self, path, writer):
		QiDataApp.__init__(self, "QiData Annotator")

		self.main_window.setWindowTitle("QiData Annotator by "+writer)
		self.writer = writer
		self.opened_qidata_object = None

		# Widget to display the file below the given path
		self.fs_explorer = FileSystemExplorer()
		self.explorer_dock = QtGui.QDockWidget("Data Explorer", parent=self.main_window)
		self.explorer_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
		self.explorer_dock.setWidget(self.fs_explorer)
		self.explorer_dock.setObjectName(self.explorer_dock.windowTitle())
		self.main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.explorer_dock)
		self.fs_explorer.setRoot(path)
		self.fs_explorer.path_selected.connect(self.setSelected)

		# Add copy-paste possibility
		self._clipboard = None
		self.copy_all_msg = QtGui.QAction("Copy all annotations", self.main_window,
		                                      shortcut="Ctrl+C",
		                                      triggered=self._copyAllAnnotations)
		self.copy_all_msg.setEnabled(False)

		self.paste_all_msg = QtGui.QAction("Paste", self.main_window,
		                                      shortcut="Ctrl+V",
		                                      triggered=self._pasteAllAnnotations)
		self.paste_all_msg.setEnabled(False)

		self.main_window.file_menu.addAction(self.copy_all_msg)
		self.main_window.file_menu.addAction(self.paste_all_msg)

	# ──────────
	# Public API

	def setSelected(self, path):
		if self.opened_qidata_object is not None:
			# Save the current disposition
			self.main_window._save_settings()

			# Request a file closure
			event = QtGui.QCloseEvent()
			if not self.main_window.main_widget.closeEvent(event):
				self.fs_explorer._cancelSelectionChange()
				return
			else:
				self.opened_qidata_object.close()
				self.opened_qidata_object = None

		if qidata.isSupportedDataFile(path):
			# Open a new file
			self.opened_qidata_object = qidata.open(path, "w")
			try:
				self.main_window.main_widget = QiDataSensorWidget(
			                                   self.opened_qidata_object,
			                                   self.writer
			                               )
			except Exception:
				self.opened_qidata_object.close()
				self.opened_qidata_object = None
				raise

		elif os.path.isdir(path):
			if not qidata.isDataset(path):
				answer = QtGui.QMessageBox.question(
				    self.main_window,
				    "Not a QiDataSet yet",
				    "Do you want to turn this folder into a QiDataSet ?",
				    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
				)
				if answer != QtGui.QMessageBox.Yes:
					return

			self.opened_qidata_object = qidata.QiDataSet(path, "w")
			self.main_window.main_widget = QiDataSetWidget(
			                                   self.opened_qidata_object,
			                                   self.writer
			                               )
		self.copy_all_msg.setEnabled(True)

	def run(self):
		try:
			super(App, self).run()
		finally:
			if self.opened_qidata_object is not None:
				self.opened_qidata_object.close()

	# ───────────
	# Private API

	def _copyAllAnnotations(self):
		w = self.main_window.main_widget
		if w is not None\
		   and w.displayed_qidata_object is not None:
				if w.displayed_qidata_object.annotations.has_key(self.writer):
					self._clipboard = w.displayed_qidata_object.annotations[self.writer]
				if self._clipboard is not None:
					self.paste_all_msg.setEnabled(True)

	def _pasteAllAnnotations(self):
		w = self.main_window.main_widget
		if w is not None\
		   and w.displayed_qidata_object is not None\
		   and self._clipboard is not None:
			for annotation_bins in self._clipboard.values():
				for annot in annotation_bins:
					w.displayed_qidata_object.addAnnotation(self.writer,
					                                        annot[0],
					                                        annot[1])

					w.qidata_widget._addAnnotationItemOnView(
					    annot[1], (self.writer, annot[0])
					)

def main(args):
	qidata_app = App(args.path, args.writer)
	try:
		qidata_app.run()
	except KeyboardInterrupt:
		pass

# ─────────────────────────────
# Definitions for Qidata plugin

DESCRIPTION = "Opens a viewer to display a QiDataSensorFile"

def make_command_parser(parser=argparse.ArgumentParser(description=DESCRIPTION)):
	writer_arg = parser.add_argument("writer",
	                                 help="Name of the annotator"
	                                )
	path_arg = parser.add_argument("path", help="Root of the tree to display")
	parser.set_defaults(func=main)
	return parser

# ───────────────────
# Add a main launcher

if __name__ == "__main__":
	parser = make_command_parser()
	parsed_args = parser.parse_args(sys.argv[1:])
	parsed_args.func(parsed_args)