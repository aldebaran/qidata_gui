# -*- coding: utf-8 -*-

# Standard Library
import sys
# Qt
from PySide import QtGui, QtCore
# qidata
from .data_explorer import DataExplorer
from PySide.QtGui import QWidget

class QiDataMainWindow(QtGui.QMainWindow):
	def __init__(self, desktop_geometry = None):
		super(QiDataMainWindow, self).__init__()
		self.setWindowTitle("qidata annotate")
		self.printer = QtGui.QPrinter()

		# ───────
		# Widgets

		self.data_explorer = DataExplorer()
		self.explorer_dock = QtGui.QDockWidget("Data Explorer", parent=self)
		self.explorer_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
		self.explorer_dock.setWidget(self.data_explorer)
		self.explorer_dock.setObjectName(self.explorer_dock.windowTitle())
		self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.explorer_dock)

		self.visualization_widget = QWidget()

		# ───────
		# Actions

		self.exit_action = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
		self.toggle_explorer_action = QtGui.QAction("Toggle &Explorer", self,
		                                            shortcut="Ctrl+E",
		                                            triggered=self.explorer_dock.toggleViewAction().trigger)

		# ─────
		# Menus

		self.file_menu = QtGui.QMenu("&File", self)
		self.file_menu.addAction(self.exit_action)

		self.view_menu = QtGui.QMenu("&View", self)
		self.view_menu.addAction(self.toggle_explorer_action)

		self.menuBar().addMenu(self.file_menu)
		self.menuBar().addMenu(self.view_menu)

		# ──────────────────
		# State and geometry

		self.setDefaultGeometry(desktop_geometry)
		self.__restore()

	# ──────────
	# Properties

	@property
	def visualization_widget(self):
		return self._visualization_widget

	@visualization_widget.setter
	def visualization_widget(self, new_visualization_widget):
		self._visualization_widget = new_visualization_widget
		self.setCentralWidget(self._visualization_widget)

	# ─────────────────────
	# QMainWindow overrides

	def closeEvent(self, event):
		self.__save()
		QtGui.QMainWindow.closeEvent(self, event)

	# ────────────
	# Geometry API

	def setDefaultGeometry(self, desktop_geometry = None):
		if not QtCore.QSettings().contains("geometry"):
			self.resize(800, 600)
			if desktop_geometry:
				self.center(desktop_geometry)

	def center(self, desktop_geometry):
		self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
		                                          self.size(), desktop_geometry))

	# ───────
	# Helpers

	def __save(self):
		QtCore.QSettings().setValue("geometry", self.saveGeometry())
		QtCore.QSettings().setValue("windowState", self.saveState())

	def __restore(self):
		self.restoreGeometry(QtCore.QSettings().value("geometry"))
		self.restoreState(QtCore.QSettings().value("windowState"))
