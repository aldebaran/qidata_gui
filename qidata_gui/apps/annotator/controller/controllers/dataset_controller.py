# -*- coding: utf-8 -*-

# qidata
from qidata import qidataset

# local
from ..annotation_controller import AnnotationController
from ...view import AnnotationInterface

class DataSetController(AnnotationController):

	# ───────────
	# Constructor

	def __init__(self, source_path, user_name):
		AnnotationController.__init__(self, source_path, user_name)

	# ───────────────
	# Private methods

	def _loadFileInformation(self):
		with qidataset.QiDataSet(self.source_path, "r") as _ds:
			self.annotators = _ds.annotators
			self.metadata = _ds.metadata
			self.content = _ds.content
			self.view = AnnotationInterface(_ds)

	def _saveFileInformation(self):
		with qidataset.QiDataSet(self.source_path, "w") as _file:
			_file.metadata = self._cleanEmptyElements(self.metadata)
			_file._content = self.content

	def _makeLocation(self, coordinates):
		return None