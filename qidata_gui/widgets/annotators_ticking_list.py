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

	def __init__(self, has_writer, annotators, parent=None):
		"""
		GeneralMetadataList constructor

		:param has_writer: True if someone is the writer (if True, writer is the first annotator)
		:param parent:  Parent of this widget
		"""
		QtGui.QListWidget.__init__(self, parent)
		self.annotators = annotators

		## VIEW DEFINITION
		if has_writer:
			offset = 1
			item = QtGui.QListWidgetItem(self.annotators[0], parent=self)
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable)
			item.setCheckState(QtCore.Qt.Checked)
			self.addItem(item)
		else:
			offset = 0

		for annotator_index in range(offset, len(self.annotators)):
			item = QtGui.QListWidgetItem(self.annotators[annotator_index], parent=self)
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
			item.setCheckState(QtCore.Qt.Checked)
			self.addItem(item)

		self.itemChanged.connect(self._emitCheckedAnnotators)

	# ───────────────
	# Private methods

	def _emitCheckedAnnotators(self):
		out = list()
		for row in range(len(self.annotators)):
			it = self.item(row)
			if it.checkState() == QtCore.Qt.Checked:
				out.append(it.text())
		self.annotatorsTickedChanged.emit(out)
