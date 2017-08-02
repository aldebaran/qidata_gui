# -*- coding: utf-8 -*-

# Third-party libraries
from PySide import QtCore, QtGui

class TickableListWidget(QtGui.QListWidget):
	"""
	Widget to display a list of different elements that can be selected
	"""

	# ───────
	# Signals

	#: Emits the list of selected annotators
	tickedSelectionChanged = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, tickable_elements, ticked_elements=[], parent=None):
		"""
		TickableListWidget constructor

		:param tickable_elements: List of elements that can be ticked
		:type tickable_elements: list
		:param ticked_elements: List of elements always ticked
		:type ticked_elements: list
		:param parent: Parent of this widget
		:type parent: PySide.QtGui.QWidget
		"""
		QtGui.QListWidget.__init__(self, parent)
		self.num_elem = len(ticked_elements) + len(tickable_elements)

		for i in range(0, len(ticked_elements)):
			item = QtGui.QListWidgetItem(ticked_elements[i], parent=self)
			item.setFlags(QtCore.Qt.ItemIsSelectable\
			                | QtCore.Qt.ItemIsUserCheckable)
			item.setCheckState(QtCore.Qt.Checked)
			self.addItem(item)

		for i in range(0, len(tickable_elements)):
			item = QtGui.QListWidgetItem(tickable_elements[i], parent=self)
			item.setFlags(QtCore.Qt.ItemIsSelectable\
			                | QtCore.Qt.ItemIsUserCheckable\
			                | QtCore.Qt.ItemIsEnabled
			             )
			item.setCheckState(QtCore.Qt.Checked)
			self.addItem(item)

		self.itemChanged.connect(self._emitCheckedAnnotators)

	# ───────────
	# Private API

	def _emitCheckedAnnotators(self):
		out = list()
		for row in range(self.num_elem):
			it = self.item(row)
			if it.checkState() == QtCore.Qt.Checked:
				out.append(it.text())
		self.tickedSelectionChanged.emit(out)
