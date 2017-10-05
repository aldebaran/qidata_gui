# -*- coding: utf-8 -*-

# Copyright (c) 2017, Softbank Robotics Europe
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
