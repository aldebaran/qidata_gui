# -*- coding: utf-8 -*-

# qidata
from qidata import qidataset

# local
from qidata_widget import QiDataWidget, raiseIfReadOnly

class QiDataSetWidget(QiDataWidget):
	"""
	Specialization of ``QiDataWidget`` for data sets display
	"""

	# ─────────────────
	# Overriden methods

	def _loadFileInformation(self):
		with qidataset.QiDataSet(self.source_path, "r") as _ds:
			self.annotators = _ds.annotators
			self.annotators.sort()
			if self.writer in self.annotators:
				self.annotators.remove(self.writer)
			if not self.read_only:
				self.annotators.insert(0, self.writer)
			self.metadata = _ds.metadata
			self.content = _ds.content
			self.displayed_object = _ds

		if not self.read_only:
			self._allocateSpaceForUserAnnotations(self.writer)

	@raiseIfReadOnly
	def _saveFileInformation(self):
		self._deallocateUnusedSpaceForUserAnnotations()
		with qidataset.QiDataSet(self.source_path, "w") as _ds:
			_ds.metadata = self.metadata
			_ds._content = self.content
		self._allocateSpaceForUserAnnotations(self.writer)

	def _makeLocation(self, coordinates):
		return None