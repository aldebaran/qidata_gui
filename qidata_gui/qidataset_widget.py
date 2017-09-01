# -*- coding: utf-8 -*-

# Standard libraries
import os

# Third-party libraries
from PySide import QtCore, QtGui
import qidata
from qidata import QiDataSet
from strong_typing import ObjectDisplayWidget

# Local modules
from qidata_gui import RESOURCES_DIR
from qidataframe_widget import QiDataFrameWidget

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

		self._frame_widget_location = 0



	def displayFrame(self, qidataframe):
		# If a frame is displayed, remove it
		self.hideFrame()

		# Add a new widget to display the frame
		self.addWidget(
		    QiDataFrameWidget(
		        self.qidataset,
		        qidataframe,
		        self.writer,
		    )
		)

	def hideFrame(self):
		if self.count()>self._frame_widget_location:
			# If there is already a displayed frame, remove it
			w = self.widget(self._frame_widget_location)
			w.setParent(None) # take it out of the view
			w.deleteLater() # destroy it

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
		self.writer = writer

		# ──────────
		# Create GUI
		# ──────────

		# Left-most widget: A set of widgets
		self.left_most_widget = QtGui.QSplitter(QtCore.Qt.Vertical, self)

			# Dataset children display
		self.datatypes_list = QtGui.QTreeWidget()
		self.datatypes_list.setColumnCount(1)
		self.datatypes_list.setHeaderHidden(False)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Data types available")
		self.datatypes_list.setHeaderItem(header_item)
		self.datatypes_list.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
		self.left_most_widget.addWidget(self.datatypes_list)

			# Dataset content display
		self.content_tree = QtGui.QTreeWidget()
		self.content_tree.setColumnCount(3)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Annotator")
		header_item.setText(1, "Annotation type")
		header_item.setText(2, "Is total ?")
		self.content_tree.setHeaderItem(header_item)
		self.left_most_widget.addWidget(self.content_tree)

			# Frames display
		# self.frames_list = SelectableListWidget()
		self.frames_list = QtGui.QTreeWidget()
		self.frames_list.setColumnCount(1)
		self.frames_list.setHeaderHidden(False)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Frames defined")
		self.frames_list.setHeaderItem(header_item)
		self.left_most_widget.addWidget(self.frames_list)

			# Button bar (refresh and frame control)
		self.buttons_widget = QtGui.QWidget(self)
		self.buttons_layout = QtGui.QHBoxLayout(self)
		self.buttons_widget.setLayout(self.buttons_layout)

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

				# "Add" button
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
		self.plus_button.setEnabled(True)
		# There is no need to have a writer to be allowed to add a frame, as
		# frame creation is not signed. However, a writer will be needed to
		# annotate any frame (new or not)

				# "Delete" button
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
		self.minus_button.setEnabled(False)

		self.buttons_layout.addWidget(self.plus_button)
		self.buttons_layout.addWidget(self.minus_button)
		self.buttons_layout.addWidget(self.refresh_button)
		self.left_most_widget.addWidget(self.buttons_widget)
		self.addWidget(self.left_most_widget)

		# Central widget
		self.central_widget = CentralWidget(self.qidataset, self.writer, self)
		self.addWidget(self.central_widget)

		# Right-most widget: A displayer for selected annotation
		self.context_displayer = ObjectDisplayWidget(self)
		self.context_displayer.setToolTip("Dataset context")
		self.addWidget(self.context_displayer)
		self.context_displayer.read_only = self.qidataset.read_only
		self.context_displayer.data = self.qidataset.context

		self._refreshGuiContent()

		# ──────────
		# END OF GUI
		# ──────────

		self.refresh_button.clicked.connect(self._refreshDataset)
		self.plus_button.clicked.connect(self._addFrame)
		self.frames_list.itemActivated.connect(self._displayFrame)
		self.frames_list.itemClicked.connect(self._selectFrame)
		self.minus_button.clicked.connect(
		    lambda: self._removeFrame(
		        self.frames_list.currentItem()
		    )
		)


	# ──────────
	# Properties

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
			# self.global_annotation_displayer\
		 #        .addItem("annotation", annotation_details)
		self.frames_list.resizeColumnToContents(0)
		self.frames_list.update()

	def _displayFrame(self, item, column):
		if item is not None:
			self.central_widget.displayFrame(item.data(0, QtCore.Qt.UserRole))

	def _selectFrame(self, item, column):
		if not self.read_only:
			self.minus_button.setEnabled(True)

	def _removeFrame(self, item):
		self.central_widget.hideFrame()
		self.qidataset.removeFrame(
		    *(item.data(0, QtCore.Qt.UserRole).files)
		)
		index = self.frames_list.indexOfTopLevelItem(item)
		self.frames_list.takeTopLevelItem(index)

	# ─────
	# Slots

	def closeEvent(self, event):
		QtGui.QSplitter.closeEvent(self, event)
		return True