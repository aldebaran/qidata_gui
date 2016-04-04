#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import sys
# PySide
from PySide import QtGui, QtCore
# qidata
from . import dataset_explorer, image_annotation

class QiDataMainWindow(QtGui.QMainWindow):
	def __init__(self, desktop_geometry = None):
		super(QiDataMainWindow, self).__init__()

		self.setWindowTitle("qidata annotate")

		self.printer = QtGui.QPrinter()

		self.createWidgets()
		self.createActions()
		self.createMenus()
		self.defaultGeometry(desktop_geometry)
		self.restore()

	def closeEvent(self, event):
		self.save()
		QtGui.QMainWindow.closeEvent(self, event)

	def save(self):
		self.persistent_settings.setValue("geometry", self.saveGeometry())
		self.persistent_settings.setValue("windowState", self.saveState())

	def restore(self):
		self.restoreGeometry(self.persistent_settings.value("geometry"))
		self.restoreState(self.persistent_settings.value("windowState"))

	@property
	def persistent_settings(self):
		return QtCore.QSettings()

	def defaultGeometry(self, desktop_geometry = None):
		if not self.persistent_settings.contains("geometry"):
			self.resize(800, 600)
			if desktop_geometry:
				self.center(desktop_geometry)

	def center(self, desktop_geometry):
		self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
		                                          self.size(), desktop_geometry))

	def createActions(self):
		self.exit_action = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
		self.toggle_explorer_action = QtGui.QAction("Toggle &Explorer", self,
		                                            shortcut="Ctrl+E",
		                                            triggered=self.explorer_dock.toggleViewAction().trigger)

	def createMenus(self):
		self.file_menu = QtGui.QMenu("&File", self)
		self.file_menu.addAction(self.exit_action)

		self.view_menu = QtGui.QMenu("&View", self)
		self.view_menu.addAction(self.toggle_explorer_action)

		self.menuBar().addMenu(self.file_menu)
		self.menuBar().addMenu(self.view_menu)

	def createWidgets(self):
		explorer = dataset_explorer.DatasetExplorer()
		self.explorer_dock = QtGui.QDockWidget("Dataset Explorer", parent=self)
		self.explorer_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
		self.explorer_dock.setWidget(explorer)
		self.explorer_dock.setObjectName(self.explorer_dock.windowTitle())
		self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.explorer_dock)

		image_annotator = image_annotation.ImageAnnotation()
		self.setCentralWidget(image_annotator)
