# -*- coding: utf-8 -*-

# Standard Library
import os.path
# Qt
from PySide.QtCore import QDir
from PySide.QtCore import Signal, Slot
from PySide.QtGui import QWidget, QFileSystemModel, QTreeView, QSortFilterProxyModel, QItemSelectionModel
# qidata
from ..models import data

class DataFSModel(QSortFilterProxyModel):
	def __init__(self):
		super(DataFSModel, self).__init__()

	# ───────────────────────────────
	# QSortFilterProxyModel overrides

	def filterAcceptsRow(self, source_row, source_parent):
		index = self.sourceModel().index(source_row, 0, source_parent)
		path = self.sourceModel().filePath(index)
		return  os.path.isdir(path) or data.isMetadataFile(path) or data.isSupported(path)

class DataExplorer(QTreeView):
	# ───────
	# Signals

	path_selected = Signal(str)

	# ───────────
	# Constructor

	def __init__(self, root = "."):
		super(DataExplorer, self).__init__()

		self.setRoot(root)
		self.__setParameters()
		self._previousIndex = None
		self._ignore_events = False

	# ────────
	# Main API

	def setRoot(self, new_root):
		self.__fs_model = QFileSystemModel()
		self.__fs_model.setRootPath(new_root)
		self.data_fs_model = DataFSModel()
		self.data_fs_model.setSourceModel(self.__fs_model)
		self.setModel(self.data_fs_model)
		self.setRootIndex(self.data_fs_model.mapFromSource(self.__fs_model.index(new_root)))

	def _cancelSelectionChange(self):
		self._ignore_events = True
		self.selectionModel().select(self._previousIndex, QItemSelectionModel.ClearAndSelect)
		self._ignore_events = False

	# ───────────────────
	# QTreeView overrides

	def selectionChanged(self, selected, deselected):
		super(DataExplorer, self).selectionChanged(selected, deselected)
		if self._ignore_events:
			return
		indexes = selected.indexes()
		index = indexes[0]
		path = self.__fs_model.filePath(self.data_fs_model.mapToSource(index))
		self._previousIndex = deselected
		self.path_selected.emit(path)


	# ───────
	# Helpers

	def __setParameters(self):
		self.setHeaderHidden(True)
		for s in range(1,self.header().count()): self.setColumnHidden(s, True)
		self.setAnimated(True)
