# -*- coding: utf-8 -*-

# Third-party libraries
from PySide import QtCore, QtGui
import qidata
from qidata import MetadataType, makeMetadataObject, ReadOnlyException
from strong_typing import ObjectDisplayWidget

# Local modules
from _subwidgets import TickableListWidget
from _subwidgets import SelectableListWidget
from _subwidgets import RawDataDisplayWidget

import exceptions

class QiDataSensorWidget(QtGui.QSplitter):
	"""
	General widget to display QiDataSensorObject.
	"""

	# ───────────
	# Constructor

	def __init__(self, qidata_sensor_object, parent=None):
		"""
		QiDataSensorWidget constructor

		:param qidata_sensor_object: Object to display
		:type qidata_sensor_object: qidata.qidatasensorobject.QiDataSensorObject
		:param parent:  Parent of this widget
		:type parent: PySide.QtGui.QWidget
		"""
		QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal, parent)

		# Store given inputs
		self.displayed_object = qidata_sensor_object

		# ──────────
		# Create GUI
		# ──────────

		# Left-most widget: A set of widgets
		self.left_most_widget = QtGui.QSplitter(QtCore.Qt.Vertical, self)

			# A tickable list to select the annotators to display
		self.annotators_list = TickableListWidget(
		                           self.displayed_object.annotators,
		                           parent=self
		                       )
		self.left_most_widget.addWidget(self.annotators_list)

			# A list of un-localized annotations
		self.global_annotation_displayer = SelectableListWidget(self)
		self.left_most_widget.addWidget(self.global_annotation_displayer)

			# A widget to display the object timestamp
		self.timestamp_displayer = ObjectDisplayWidget(self)
		self.left_most_widget.addWidget(
		    self.timestamp_displayer
		)
		self.timestamp_displayer.read_only = True
		self.timestamp_displayer.data = self.displayed_object.timestamp

			# A widget to display the object transform
		self.transform_displayer = ObjectDisplayWidget(self)
		self.left_most_widget.addWidget(
		    self.transform_displayer
		)
		self.transform_displayer.read_only = True
		self.transform_displayer.data = self.displayed_object.transform
		self.addWidget(self.left_most_widget)


		# Central widget: Raw data viewer creation
		self.raw_data_viewer = RawDataDisplayWidget(
		                           self,
		                           self.displayed_object.type,
		                           self.displayed_object.raw_data
		                       )

		self.addWidget(self.raw_data_viewer)

		# Right-most widget: A displayer for selected annotation
		self.right_most_widget = QtGui.QWidget(self)
		self.right_most_layout = QtGui.QVBoxLayout(self)

		self.type_selector = QtGui.QComboBox(self.right_most_widget)
		self.type_selector.setEnabled(False)
		self.type_selector.addItems(
		    map(str, list(MetadataType))
		)
		self.right_most_layout.addWidget(self.type_selector)

		self.annotation_displayer = ObjectDisplayWidget(self)
		self.annotation_displayer.read_only = True
		self.right_most_layout.addWidget(self.annotation_displayer)

		self.right_most_widget.setLayout(self.right_most_layout)
		self.addWidget(self.right_most_widget)

		# ──────────
		# END OF GUI
		# ──────────

		# Display object annotations
		self._showAnnotationsFrom(self.displayed_object.annotators)

		# Bind signals
		self.raw_data_viewer.itemSelected.connect(self._displayLocalizedInfo)
		self.global_annotation_displayer\
		    .itemSelected.connect(self._displayGlobalInfo)
		self.annotators_list\
		    .tickedSelectionChanged.connect(self._showAnnotationsFrom)

	# ───────────
	# Private API

	def _addAnnotationItemOnView(self, annotation_item):
		"""
		Add a metadata item on the view.

		This method adds an item representing the metadata location but
		does not display the object details.

		:param annotation_item:  The item to be shown
		:return:  Reference to the widget representing the metadata

		.. note::
		The returned reference is handy to connect callbacks on the
		widget signals. This reference is also needed to remove the object.
		"""
		if annotation_item[1] is None:
			r = self.global_annotation_displayer\
			        .addItem("annotation", annotation_item[0])
		else:
			r = self.raw_data_viewer\
			        .addItem(annotation_item[1], annotation_item[0])
		return r

	def _displayLocalizedInfo(self, info):
		self.global_annotation_displayer.deselectAll()
		self._displayInfo(info)

	def _displayGlobalInfo(self, info):
		self.raw_data_viewer.deselectAll()
		self._displayInfo(info)

	def _displayInfo(self, info):
		self.type_selector.setCurrentIndex(
		    self.type_selector.findText(type(info).__name__)
		)
		self.annotation_displayer.data = info

	def _showAnnotationsFrom(self, requested_annotators):
		# Clear
		self.global_annotation_displayer.clearAllItems()
		self.raw_data_viewer.clearAllItems()
		self.annotation_displayer.data = None

		# Display
		annotators_to_display = set(requested_annotators).intersection(
		                            set(self.displayed_object.annotators)
		                        )
		annotations = self.displayed_object.annotations
		annotations_list = [
		    annotation\
		    for annotator in annotators_to_display\
		    for annotation_list in annotations[annotator].values()\
		    for annotation in annotation_list
		]
		for m in annotations_list:
			self._addAnnotationItemOnView(m)
