# -*- coding: utf-8 -*-

# Standard libraries
import os

# Third-party libraries
from PySide import QtCore, QtGui
import qidata
from qidata import MetadataType, makeMetadataObject, ReadOnlyException
from strong_typing import ObjectDisplayWidget

# Local modules
from qidata_gui import RESOURCES_DIR
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

	def __init__(self, qidata_sensor_object, writer="", parent=None):
		"""
		QiDataSensorWidget constructor

		:param qidata_sensor_object: Object to display
		:type qidata_sensor_object: qidata.qidatasensorobject.QiDataSensorObject
		:param writer: Person modifying the object (necessary to add annotations)
		:type writer: str
		:param parent:  Parent of this widget
		:type parent: PySide.QtGui.QWidget
		"""
		QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal, parent)

		# Store given inputs
		self.displayed_object = qidata_sensor_object
		self._read_only = qidata_sensor_object.read_only
		self._has_writer = (writer != "")
		self.writer = writer

		# ──────────
		# Create GUI
		# ──────────

		# Left-most widget: A set of widgets
		self.left_most_widget = QtGui.QSplitter(QtCore.Qt.Vertical, self)

			# A tickable list to select the annotators to display
		annotators = self.displayed_object.annotators
		if self._has_writer and self.writer in annotators:
		    annotators.remove(self.writer)
		self.annotators_list = TickableListWidget(
		                           annotators,
		                           [self.writer] if self._has_writer else [],
		                           parent=self
		                       )
		self.left_most_widget.addWidget(self.annotators_list)

			# A list of un-localized annotations with add/remove buttons
		self.global_annotations_widget = QtGui.QWidget(self)
		self.global_annotations_layout = QtGui.QVBoxLayout(self)
		self.global_annotation_displayer = SelectableListWidget(self)

			# Two buttons to add/remove an annotation from the list
		self.buttons_widget = QtGui.QWidget(self)

				# "Plus" button
		self.plus_button = QtGui.QPushButton("", self.buttons_widget)
		plus_ic_path = os.path.join(RESOURCES_DIR, "add.png")
		plus_ic = QtGui.QIcon(plus_ic_path)
		self.plus_button.setFixedSize(
		    plus_ic.actualSize(
		        plus_ic.availableSizes()[0]
		    )
		)
		self.plus_button.setText("")
		self.plus_button.setToolTip("Add an unlocalized annotation")
		self.plus_button.setIcon(plus_ic)
		self.plus_button.setIconSize(plus_ic.availableSizes()[0])
		self.plus_button.setEnabled(self._has_writer)

				# "Minus" button
		self.minus_button = QtGui.QPushButton("", self.buttons_widget)
		minus_ic_path = os.path.join(RESOURCES_DIR, "delete.png")
		minus_ic = QtGui.QIcon(minus_ic_path)
		self.minus_button.setFixedSize(
		    minus_ic.actualSize(
		        minus_ic.availableSizes()[0]
		    )
		)
		self.minus_button.setText("")
		self.minus_button.setToolTip("Remove an unlocalized annotation")
		self.minus_button.setIcon(minus_ic)
		self.minus_button.setIconSize(minus_ic.availableSizes()[0])
		self.minus_button.setEnabled(False)

		# Aggregation
		self.buttons_layout = QtGui.QHBoxLayout(self)
		self.buttons_layout.addWidget(self.plus_button)
		self.buttons_layout.addWidget(self.minus_button)
		self.buttons_widget.setLayout(self.buttons_layout)
		self.global_annotations_layout.addWidget(self.global_annotation_displayer)
		self.global_annotations_layout.addWidget(self.buttons_widget)
		self.global_annotations_widget.setLayout(self.global_annotations_layout)
		self.left_most_widget.addWidget(self.global_annotations_widget)

			# A widget to display the object timestamp
		self.timestamp_displayer = ObjectDisplayWidget(self)
		self.left_most_widget.addWidget(
		    self.timestamp_displayer
		)
		self.timestamp_displayer.read_only = self._read_only
		self.timestamp_displayer.data = self.displayed_object.timestamp

			# A widget to display the object transform
		self.transform_displayer = ObjectDisplayWidget(self)
		self.left_most_widget.addWidget(
		    self.transform_displayer
		)
		self.transform_displayer.read_only = self._read_only
		self.transform_displayer.data = self.displayed_object.transform
		self.addWidget(self.left_most_widget)


		# Central widget: Raw data viewer creation
		self.raw_data_viewer = RawDataDisplayWidget(
		                           self,
		                           self.displayed_object.type,
		                           self.displayed_object.raw_data
		                       )
		self.raw_data_viewer.read_only = self._read_only
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
		self.annotation_displayer.read_only = self._read_only
		self.right_most_layout.addWidget(self.annotation_displayer)

		self.right_most_widget.setLayout(self.right_most_layout)
		self.addWidget(self.right_most_widget)

		# ──────────
		# END OF GUI
		# ──────────

		# Display object annotations
		self._showAnnotationsFrom(self.displayed_object.annotators)

		# Bind signals
		self.raw_data_viewer.objectTypeChanged.connect(self._objectTypeChanged)
		self.raw_data_viewer.itemSelected.connect(self._displayLocalizedInfo)
		self.raw_data_viewer.itemAdditionRequested.connect(self._addAnnotation)
		self.raw_data_viewer.itemDeletionRequested.connect(
		    self._deleteLocalizedAnnotation
		)

		self.plus_button.clicked.connect(lambda: self._addAnnotation(None))
		self.minus_button.clicked.connect(
		    lambda: self._deleteGlobalAnnotation(
		        self.global_annotation_displayer.currentItem()
		    )
		)

		self.global_annotation_displayer\
		    .itemSelected.connect(self._displayGlobalInfo)
		self.annotators_list\
		    .tickedSelectionChanged.connect(self._showAnnotationsFrom)

		self.type_selector.currentIndexChanged["QString"].connect(
			self._annotationTypeChanged
		)

		# Restore saved geometry
		settings = QtCore.QSettings("Softbank Robotics", "QiDataSensorWidget")
		self.restoreGeometry(settings.value("geometry"))
		self.restoreState(settings.value("windowState"))
		self.left_most_widget.restoreGeometry(settings.value("geometry/left"))
		self.left_most_widget.restoreState(settings.value("windowState/left"))

	# ──────────
	# Properties

	@property
	def displayed_qidata_object(self):
		return self.displayed_object

	@property
	def qidata_widget(self):
		return self

	@property
	def read_only(self):
		return self._read_only

	# ───────────
	# Private API

	def _addAnnotation(self, location):
		annot = makeMetadataObject(self.type_selector.currentText())
		self.displayed_object.addAnnotation(self.writer, annot, location)
		self._addAnnotationItemOnView(location, (self.writer, annot))

	def _addAnnotationItemOnView(self, location, annotation_details):
		"""
		Add a metadata item on the view.

		This method adds an item representing the metadata location but
		does not display the object details.

		:param location: The position where to display the item
		:type location: list or None
		:param annotation_details: Contents of the annotation
		:type annotation_details: list
		:return:  Reference to the widget representing the metadata

		.. note::
		The returned reference is handy to connect callbacks on the
		widget signals. This reference is also needed to remove the object.
		"""
		if location is None:
			r = self.global_annotation_displayer\
			        .addItem("annotation", annotation_details)
		else:
			r = self.raw_data_viewer\
			        .addItem(location, annotation_details)
		return r

	def _annotationTypeChanged(self, new_type):
		if new_type == type(self.annotation_displayer.data).__name__:
			# Type did not really changed, maybe user cancelled a change
			# Ignore the event
			return
		response = QtGui.QMessageBox.warning(
		               self,
		               "Change annotation type",
		               "Changing an annotation type deletes the information \
		               previsouly entered. Are you sure you want to change \
		               this annotation's type ?",
		               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
		           )
		if QtGui.QMessageBox.Yes == response:
			if self.global_annotation_displayer.currentItem():
				item = self.global_annotation_displayer.currentItem()
				annotator, annotation = item.value
				self.displayed_object.removeAnnotation(annotator, annotation)

				annotation = makeMetadataObject(new_type)
				self.displayed_object.addAnnotation(annotator, annotation)
				item.value = (annotator, annotation)
				self.annotation_displayer.data = annotation

			else:
				item = self.raw_data_viewer._widget.scene._selectedItem
				annotator, annotation = item.info
				location = item.coordinates
				self.displayed_object.removeAnnotation(annotator,
				                                       annotation,
				                                       location)

				annotation = makeMetadataObject(new_type)
				self.displayed_object.addAnnotation(annotator,
				                                    annotation,
				                                    location)

				item.info = (annotator, annotation)
				self.annotation_displayer.data = annotation

		else:
			self.type_selector.setCurrentIndex(
			    self.type_selector.findText(
			        type(self.annotation_displayer.data).__name__
			    )
			)

	def _clearDisplayer(self):
		self.type_selector.setEnabled(False)
		self.annotation_displayer.data = None

	def _deleteGlobalAnnotation(self, global_item):
		if self._askForDeletionConfirmation():
			self.displayed_object.removeAnnotation(*(global_item.value))
			self.global_annotation_displayer.removeSelectedItem()
			self._clearDisplayer()

	def _deleteLocalizedAnnotation(self, localized_item):
		if self._askForDeletionConfirmation():
			self.displayed_object.removeAnnotation(localized_item.info[0],
			                                       localized_item.info[1],
			                                       localized_item.coordinates)
			self.raw_data_viewer.removeItem(localized_item)
			self._clearDisplayer()

	def _objectTypeChanged(self, new_type):
		if new_type == str(self.displayed_object.type):
			# Type did not really changed, maybe user cancelled a change
			# Ignore the event
			return
		try:
			self.displayed_object.type = new_type
		except TypeError:
			response = QtGui.QMessageBox.critical(
			               self,
			               "Wrong type",
			               "The selected type cannot be selected",
			               QtGui.QMessageBox.Ok
			           )
			self.raw_data_viewer.setType(
			    str(self.displayed_object.type)
			)

	def _askForDeletionConfirmation(self):
		response = QtGui.QMessageBox.warning(
		               self,
		               "Suppression",
		               "Are you sure you want to remove this annotation ?",
		               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
		           )
		return(QtGui.QMessageBox.Yes == response)

	def _displayLocalizedInfo(self, info):
		self.global_annotation_displayer.deselectAll()
		self.minus_button.setEnabled(False)
		self._displayInfo(info[1]) # info[0] is the annotator

	def _displayGlobalInfo(self, info):
		self.raw_data_viewer.deselectAll()
		if not self.read_only:
			self.minus_button.setEnabled(True)
		self._displayInfo(info[1])

	def _displayInfo(self, info):
		self.annotation_displayer.data = info
		self.type_selector.setCurrentIndex(
		    self.type_selector.findText(type(info).__name__)
		)
		self.type_selector.setEnabled(not self.read_only)

	def _showAnnotationsFrom(self, requested_annotators):
		# Clear
		self.global_annotation_displayer.clearAllItems()
		self.raw_data_viewer.clearAllItems()
		self._clearDisplayer()

		# Display
		annotators_to_display = set(requested_annotators).intersection(
		                            set(self.displayed_object.annotators)
		                        )
		annotations = self.displayed_object.annotations
		for annotator in annotators_to_display:
			for annotation_type in annotations[annotator].keys():
				for annotation in self.displayed_object.getAnnotations(
				        annotator,
				        annotation_type
				    ):
					self._addAnnotationItemOnView(
					    annotation[1], (annotator, annotation[0])
					)

	def _checkIfFileMustBeSavedAndClosed(self):
		"""
		Asks user through a pop-up if the modifications on the object must be
		saved or not. This is only possible if the object is a
		:class:`qidata.qidatasensorfile.QiDataSensorFile` otherwise the pop-up
		only asks confirmation before closing.

		.. note::
			There are a few conditions under which the pop-up does not appear
			- If the file is closed
			- If the object is read-only
		"""
		if hasattr(self.displayed_object, "closed") and self.displayed_object.closed:
			return True

		if self.displayed_object.read_only:
			return True

		if hasattr(self.displayed_object, "cancelChanges"):
			a = QtGui.QMessageBox.question(self,
			    "Leaving..",
			    "You are about to leave this file. Do you want to save your modifications ?",
			    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

			if a==QtGui.QMessageBox.Cancel:
				return False

			if a == QtGui.QMessageBox.No:
				self.displayed_object.cancelChanges()
		return True

	# ─────
	# Slots

	def closeEvent(self, event):
		if not self._checkIfFileMustBeSavedAndClosed():
			event.ignore()
			return False
		settings = QtCore.QSettings("Softbank Robotics", "QiDataSensorWidget")
		settings.setValue("geometry", self.saveGeometry())
		settings.setValue("windowState", self.saveState())
		settings.setValue("geometry/left", self.left_most_widget.saveGeometry())
		settings.setValue("windowState/left", self.left_most_widget.saveState())
		QtGui.QSplitter.closeEvent(self, event)
		return True