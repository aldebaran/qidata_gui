# -*- coding: utf-8 -*-

# Third-party libraries
from PySide import QtCore, QtGui

# Local modules
import qidata_gui

class QiDataMainWindow(QtGui.QMainWindow):
	"""
	Main window for QiData applications.
	"""

	# ───────────
	# Constructor

	def __init__(self, desktop_geometry = None):
		QtGui.QMainWindow.__init__(self)
		self.desktop_geometry = desktop_geometry

		# ───────
		# Actions

		self.exit_action = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)

		# ─────
		# Menus

		self.file_menu = QtGui.QMenu("&File", self)
		self.file_menu.addAction(self.exit_action)

		self.menuBar().addMenu(self.file_menu)

	# ──────────
	# Properties

	@property
	def main_widget(self):
		return getattr(self,"_main_widget",None)

	@main_widget.setter
	def main_widget(self, main_widget):
		self._main_widget = main_widget
		self.setCentralWidget(main_widget)
		self.setDefaultGeometry(self.desktop_geometry)
		self._restore_settings()

	# ─────
	# Slots

	def closeEvent(self, event):
		self._save_settings()
		# Let the possibility to a widget to save its geometry
		if not self.main_widget or self.main_widget.closeEvent(event):
			event.accept()
			QtGui.QMainWindow.closeEvent(self, event)
		else:
			event.ignore()

	# ──────────
	# Public API

	def setDefaultGeometry(self, desktop_geometry = None):
		if not QtCore.QSettings().contains("geometry"):
			self.resize(800, 600)
			if desktop_geometry:
				self.center(desktop_geometry)

	def center(self, desktop_geometry):
		self.setGeometry(
		    QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight,
		                             QtCore.Qt.AlignCenter,
		                             self.size(),
		                             desktop_geometry)
		)

	# ───────────
	# Private API

	def _save_settings(self):
		QtCore.QSettings().setValue("geometry", self.saveGeometry())
		QtCore.QSettings().setValue("windowState", self.saveState())

	def _restore_settings(self):
		self.restoreGeometry(QtCore.QSettings().value("geometry"))
		self.restoreState(QtCore.QSettings().value("windowState"))

class QiDataApp(QtGui.QApplication):
	"""
	QiData application base class
	"""
	def __init__(self, application_name):
		"""
		Constructs the QiData application

		:param application_name: Name to give to this application to identify it
		:type application_name: str
		"""
		QtGui.QApplication.__init__(self, [])

		# Set application metadata
		self.setOrganizationName("Softbank Robotics")
		self.setOrganizationDomain("softbankrobotics.com")
		self.setApplicationName(application_name)
		self.setApplicationVersion(qidata_gui.VERSION)

		# Prepare main window
		self.main_window = QiDataMainWindow(
		    self.desktop().availableGeometry()
		)

	# ──────────
	# Public API

	def run(self):
		self.main_window.show()
		try:
			self.exec_()
		except KeyboardInterrupt:
			pass
