#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import sys
# PySide
from PySide.QtGui import QApplication
# qidata
import qidata
from .window import QiDataMainWindow

class QiDataApp(QApplication):
	def __init__(self, root=None):
		super(QiDataApp, self).__init__([])
		self.__setMetaInfo()
		self.__setupModel()
		self.__setupGUI()

	def run(self):
		self.main_window.show()
		self.exec_()

	@property
	def desktop_geometry(self):
		return self.desktop().availableGeometry()

	# @Slot(result=int, float)
	def getFloatReturnInt(self, f):
		pass

	# ───────
	# Helpers

	def __setupModel(self, root=None):
		self.root = root

	def __setupGUI(self):
		self.main_window = QiDataMainWindow(self.desktop_geometry)

	def __setMetaInfo(self):
		self.setOrganizationName("Aldebaran")
		self.setOrganizationDomain("aldebaran.com")
		self.setApplicationName("qidata")
		self.setApplicationVersion(qidata.VERSION)
