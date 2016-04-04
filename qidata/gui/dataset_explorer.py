#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import os.path
# Qt
from PySide.QtGui import QWidget, QFileSystemModel, QTreeView, QSortFilterProxyModel
from PySide.QtCore import QDir
# qidata
from qidata import dataset

class DatasetFSModel(QSortFilterProxyModel):
	def __init__(self):
		super(DatasetFSModel, self).__init__()

	def filterAcceptsRow(self, source_row, source_parent):
		index = self.sourceModel().index(source_row, 0, source_parent)
		path = self.sourceModel().filePath(index)
		show = os.path.isdir(path) or dataset.isMetadataFile(path) or os.path.isfile(path)
		return show

class DatasetExplorer(QTreeView):
	def __init__(self):
		super(DatasetExplorer, self).__init__()

		self.fs_model = QFileSystemModel()
		self.fs_model.setRootPath(QDir.currentPath())
		self.dataset_model = DatasetFSModel();
		self.dataset_model.setSourceModel(self.fs_model);
		self.setModel(self.dataset_model)
		self.setRootIndex(self.dataset_model.mapFromSource(self.fs_model.index(QDir.currentPath())))

		self.setHeaderHidden(True)
		for s in range(1,self.header().count()): self.setColumnHidden(s, True)
		self.setAnimated(True)

	def selectionChanged(self, selected, deselected):
		super(DatasetExplorer, self).selectionChanged(selected, deselected)
		indexes = selected.indexes()
		index = indexes[0]
		path = self.fs_model.filePath(self.dataset_model.mapToSource(index))
		print "Selected", path

