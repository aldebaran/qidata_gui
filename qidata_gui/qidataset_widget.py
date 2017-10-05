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

# Standard libraries
import os

# Third-party libraries
from PySide import QtCore, QtGui
import qidata
from qidata import QiDataSet
from qidata.qidatasensorobject import QiDataSensorObject
from strong_typing import ObjectDisplayWidget

# Local modules
from qidata_gui import RESOURCES_DIR
from qidataframe_widget import QiDataFrameWidget
from qidatasensor_widget import QiDataSensorWidget
from _subwidgets import StreamViewer

class CentralWidget(QtGui.QSplitter):

	# ───────────
	# Constructor

	def __init__(self, qidataset, writer= "", parent=None):
		"""
		CentralWidget constructor

		:param qidataset: Opened QiDataSet
		:param parent:  Parent of this widget
		"""
		QtGui.QSplitter.__init__(self, QtCore.Qt.Vertical, parent)

		# Store given inputs
		self.qidataset = qidataset
		self.writer = writer

		self._sub_widget_location = 0
		self._displayed_object = None

		if len(self.qidataset.getAllStreams())>0:
			# Mark the frame widget will be the second widget
			self._sub_widget_location += 1

			# Display streams
			self._stream_viewer = StreamViewer(
			                                   self.qidataset.getAllStreams()
			                                  )
			self.addWidget(
			    self._stream_viewer
			)
			self._stream_viewer.objectSelected.connect(
			    lambda x: "" if x is None\
			                 else self.displaySensorData(
			                     qidata.open(os.path.join(self.qidataset.name, x),"w")
			                 )
			)

	def displaySensorData(self, qidatasensorobject):
		"""
		Displays a QiDataSensorObject. If a different QiDataSensorObject is
		already displayed, it is removed. If None is given, nothing is
		displayed, and any visible QiDataSensorObject is removed.

		:param qidatasensorobject: The sensor object to display
		:type qidatasensorobject: qidata.QiDataSensorObject
		"""
		if self._displayed_object is not None:
			if qidatasensorobject is not None\
			   and isinstance(self._displayed_object, QiDataSensorObject)\
			   and self._displayed_object.name == qidatasensorobject.name:
				# If the displayed object is the same as the one we want to show
				# do nothing
				return

			# If an object is displayed and is different from the one to display,
			# remove it
			self.hideSubWidget()

		if qidatasensorobject is not None:
			# Add a new widget to display the frame
			self._displayed_object = qidatasensorobject
			self.addWidget(
			    QiDataSensorWidget(
			        qidatasensorobject,
			        self.writer,
			    )
			)

	def displayFrame(self, qidataframe):
		"""
		Displays a QiDataFrame. If a different QiDataFrame is already displayed,
		it is removed. If None is given, nothing is displayed, and any visible
		QiDataFrame is removed.

		:param qidataframe: The frame to display
		:type qidataframe: qidata.QiDataFrame
		"""
		if self._displayed_object is not None:
			if qidataframe is not None\
			   and isinstance(self._displayed_object, qidata.QiDataFrame)\
			   and self._displayed_object.files == qidataframe.files:
				# If the displayed frame is the same as the one we want to show
				# do nothing
				return

			# If a frame is displayed and is different from the one to display,
			# remove it
			self.hideSubWidget()

		if qidataframe is not None:
			# Add a new widget to display the frame
			self._displayed_object = qidataframe
			self.addWidget(
			    QiDataFrameWidget(
			        self.qidataset,
			        qidataframe,
			        self.writer,
			    )
			)

	def hideSubWidget(self):
		if self._displayed_object is not None:
			# If there is already a displayed frame, remove it
			w = self.widget(self._sub_widget_location)
			w.setParent(None) # take it out of the view
			w.deleteLater() # destroy it
			if isinstance(self._displayed_object, QiDataSensorObject):
				self._displayed_object.close()
			self._displayed_object = None

class QiDataSetWidget(QtGui.QSplitter):
	"""
	Widget specialized in displaying a dataset content
	"""

	# ───────────
	# Constructor

	def __init__(self, qidataset, writer="", parent=None):
		"""
		QiDataSetWidget constructor

		:param qidataset: Opened QiDataSet
		:param parent:  Parent of this widget
		"""
		QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal, parent)

		# Store given inputs
		self.qidataset = qidataset
		self._read_only = qidataset.read_only
		self._has_writer = (writer != "")
		self._has_streams = (len(self.qidataset.getAllStreams()) > 0)
		self.writer = writer

		# ──────────
		# Create GUI
		# ──────────

		# A. Left-most widget: A set of widgets
		self.left_most_widget = QtGui.QSplitter(QtCore.Qt.Vertical, self)
		self.addWidget(self.left_most_widget)

		# A.1 Dataset children display
		self.datatypes_list = QtGui.QTreeWidget()
		self.datatypes_list.setColumnCount(1)
		self.datatypes_list.setHeaderHidden(False)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Data types available")
		self.datatypes_list.setHeaderItem(header_item)
		self.datatypes_list.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
		self.left_most_widget.addWidget(self.datatypes_list)

		# A.2 Dataset content display
		self.content_tree = QtGui.QTreeWidget()
		self.content_tree.setColumnCount(3)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Annotator")
		header_item.setText(1, "Annotation type")
		header_item.setText(2, "Is total ?")
		self.content_tree.setHeaderItem(header_item)
		self.left_most_widget.addWidget(self.content_tree)

		# A.3 Frames display (only if no stream)
		self.frames_list = QtGui.QTreeWidget()
		self.frames_list.setColumnCount(1)
		self.frames_list.setHeaderHidden(False)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Frames defined")
		self.frames_list.setHeaderItem(header_item)
		self.left_most_widget.addWidget(self.frames_list)

		# self.frames_list.itemActivated.connect(self._displayFrame)
		self.frames_list.itemClicked.connect(self._selectFrame)

		# A.4 Button bar (refresh and optional frame control)
		self.buttons_widget = QtGui.QWidget(self)
		self.buttons_layout = QtGui.QHBoxLayout()
		self.buttons_widget.setLayout(self.buttons_layout)
		self.left_most_widget.addWidget(self.buttons_widget)

		# A.4.1 "Add a frame" button
		self.plus_button = QtGui.QPushButton("", self.buttons_widget)
		plus_ic_path = os.path.join(RESOURCES_DIR, "add.png")
		plus_ic = QtGui.QIcon(plus_ic_path)
		self.plus_button.setFixedSize(
		    plus_ic.actualSize(
		        plus_ic.availableSizes()[0]
		    )
		)
		self.plus_button.setText("")
		self.plus_button.setToolTip("Add a frame")
		self.plus_button.setIcon(plus_ic)
		self.plus_button.setIconSize(plus_ic.availableSizes()[0])
		self.plus_button.clicked.connect(self._addFrame)
		# There is no need to have a writer to be allowed to add a frame, as
		# frame creation is not signed. However, a writer will be needed to
		# annotate any frame (new or not)
		self.plus_button.setEnabled(True)
		self.buttons_layout.addWidget(self.plus_button)

		# A.4.2 "Remove a frame" button
		self.minus_button = QtGui.QPushButton("", self.buttons_widget)
		minus_ic_path = os.path.join(RESOURCES_DIR, "delete.png")
		minus_ic = QtGui.QIcon(minus_ic_path)
		self.minus_button.setFixedSize(
		    minus_ic.actualSize(
		        minus_ic.availableSizes()[0]
		    )
		)
		self.minus_button.setText("")
		self.minus_button.setToolTip("Remove selected frame")
		self.minus_button.setIcon(minus_ic)
		self.minus_button.setIconSize(minus_ic.availableSizes()[0])
		self.minus_button.clicked.connect(
		    lambda: self._removeFrame(self.frames_list.currentItem())
		)
		self.minus_button.setEnabled(False)
		self.buttons_layout.addWidget(self.minus_button)

		# A.4.3 Refresh dataset content button
		self.refresh_button = QtGui.QPushButton("", self.buttons_widget)
		refresh_ic_path = os.path.join(RESOURCES_DIR, "arrow_refresh.png")
		refresh_ic = QtGui.QIcon(refresh_ic_path)
		self.refresh_button.setFixedSize(
		    refresh_ic.actualSize(
		        refresh_ic.availableSizes()[0]
		    )
		)
		self.refresh_button.setText("")
		self.refresh_button.setToolTip("Refresh dataset content")
		self.refresh_button.setIcon(refresh_ic)
		self.refresh_button.setIconSize(refresh_ic.availableSizes()[0])
		self.refresh_button.clicked.connect(self._refreshDataset)
		self.buttons_layout.addWidget(self.refresh_button)

		# Central widget
		self.central_widget = CentralWidget(self.qidataset, self.writer, self)
		self.addWidget(self.central_widget)

		# Right-most widget: A displayer for selected annotation
		self.context_displayer = ObjectDisplayWidget(self)
		self.addWidget(self.context_displayer)
		self.context_displayer.setToolTip("Dataset context")
		self.context_displayer.read_only = self.qidataset.read_only
		self.context_displayer.data = self.qidataset.context

		self._refreshGuiContent()

		# ──────────
		# END OF GUI
		# ──────────

	# ──────────
	# Properties

	@property
	def displayed_qidata_object(self):
		return self.central_widget._displayed_object

	@property
	def qidata_widget(self):
		if self.displayed_qidata_object is None:
			return None
		return self.central_widget.widget(self.central_widget._sub_widget_location)

	@property
	def read_only(self):
		return self._read_only

	# ───────────────
	# Private methods

	def _addFrame(self):
		name_filters = "QiData files (%s)"%" ".join(
		    map(
		        lambda x: x.pattern.replace(".*", "*").replace("\\.",".")[:-1],
		        qidata._LOOKUP_ITEM_MODEL.keys()
		    )
		)
		file_names = QtGui.QFileDialog.getOpenFileNames(
		    self,
		    "Choose files to add in frame",
		    self.qidataset.name,
		    name_filters
		)
		if [] == file_names[0]:
			# User canceled, do nothing
			return
		try:
			self.qidataset.createNewFrame(*(file_names[0]))
		except Exception, e:
			QtGui.QMessageBox.critical(
		        self,
		        "Error",
		        e.message
		    )
		else:
			self._refreshGuiContent()

	def _refreshDataset(self):
		self.qidataset.examineContent()
		self._refreshGuiContent()

	def _refreshGuiContent(self):

		# Clear datatypes_list contents and fill it again
		self.datatypes_list.clear()
		for child in self.qidataset.datatypes_available:
			item = QtGui.QTreeWidgetItem()
			self.datatypes_list.addTopLevelItem(item)
			item.setText(0, str(child))
		self.datatypes_list.resizeColumnToContents(0)
		self.datatypes_list.update()

		# Clear content_tree and fill it again
		self.content_tree.clear()
		content = self.qidataset.annotations_available
		for (key,value) in content.iteritems():
			item = QtGui.QTreeWidgetItem()
			self.content_tree.addTopLevelItem(item)
			item.setText(0, str(key[0]))
			item.setText(1, str(key[1]))

			inputWidget = QtGui.QCheckBox(self)
			inputWidget.setCheckState(
			    QtCore.Qt.Checked if QiDataSet.AnnotationStatus.TOTAL == value\
			                      else QtCore.Qt.Unchecked
			)
			inputWidget.stateChanged.connect(
			    lambda x: self.qidataset.setAnnotationStatus(
			        str(key[0]),
			        str(key[1]),
			        (x == QtCore.Qt.Checked)
			    )
			)
			self.content_tree.setItemWidget(item, 2, inputWidget)

		self.content_tree.resizeColumnToContents(0)
		self.content_tree.resizeColumnToContents(1)
		self.content_tree.update()

		# Clear frames_list and fill it again
		self.frames_list.clear()
		_frames = self.qidataset.getAllFrames()
		for frame_index in range(len(_frames)):
			item = QtGui.QTreeWidgetItem()
			self.frames_list.addTopLevelItem(item)
			item.setText(0, "frame_%d"%frame_index)
			item.setData(0, QtCore.Qt.UserRole, _frames[frame_index])
		self.frames_list.resizeColumnToContents(0)
		self.frames_list.update()

	def _displayFrame(self, item, column):
		if item is not None:
			self.central_widget.displayFrame(item.data(0, QtCore.Qt.UserRole))

	def _selectFrame(self, item, column):
		if not self.read_only:
			self.minus_button.setEnabled(True)

	def _removeFrame(self, item):
		self.central_widget.hideSubWidget()
		self.qidataset.removeFrame(
		    *(item.data(0, QtCore.Qt.UserRole).files)
		)
		index = self.frames_list.indexOfTopLevelItem(item)
		self.frames_list.takeTopLevelItem(index)

	# ─────
	# Slots

	def closeEvent(self, event):
		# if not self._checkIfFileMustBeSavedAndClosed():
		# 	event.ignore()
		# 	return False
		# settings = QtCore.QSettings("Softbank Robotics", "QiDataSensorWidget")
		# settings.setValue("geometry", self.saveGeometry())
		# settings.setValue("windowState", self.saveState())
		# settings.setValue("geometry/left", self.left_most_widget.saveGeometry())
		# settings.setValue("windowState/left", self.left_most_widget.saveState())
		QtGui.QSplitter.closeEvent(self, event)
		return True