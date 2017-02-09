# -*- coding: utf-8 -*-

# Qt
from PySide import QtCore, QtGui

class AnnotatorsTickingList(QtGui.QListWidget):
	"""
	Widget to display the list of annotators and to allow the user to
	select whose annotations he/she wants to see.
	"""

	# ───────
	# Signals

	#: Emits the list of selected annotators
	annotatorsTickedChanged = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, current_user, annotators, parent=None):
		"""
		GeneralMetadataList constructor

		:param current_user: Name of the person using the application
		:param parent:  Parent of this widget
		"""
		QtGui.QListWidget.__init__(self, parent)
		self.annotators = annotators
		if current_user is not None:
			self.writer = self.annotators.pop(0)
			item = QtGui.QListWidgetItem(self.writer, parent=self)
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable)
			item.setCheckState(QtCore.Qt.Checked)
			self.addItem(item)
		else:
			self.writer = None

		## VIEW DEFINITION
		for annotator in self.annotators:
			item = QtGui.QListWidgetItem(annotator, parent=self)
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
			item.setCheckState(QtCore.Qt.Checked)
			self.addItem(item)

		self.itemChanged.connect(self._emitCheckedAnnotators)

	# ───────────────
	# Private methods

	def _emitCheckedAnnotators(self):
		out = list()
		if self.writer is not None:
			offset = 1
			out.append(self.writer)
		else:
			offset = 0

		for row in range(len(self.annotators)):
			it = self.item(row + offset)
			if it.checkState() == QtCore.Qt.Checked:
				out.append(it.text())
		self.annotatorsTickedChanged.emit(out)
