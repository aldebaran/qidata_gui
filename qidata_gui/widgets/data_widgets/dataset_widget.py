# -*- coding: utf-8 -*-

# Qt
from PySide import QtCore, QtGui

class DataSetWidget(QtGui.QWidget):
	"""
	Widget specialized in displaying audio with Metadata Objects
	"""

	# ───────
	# Signals

	objectAdditionRequired = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, dataset_raw_data, parent=None):
		"""
		DataSetWidget constructor

		:param dataset_raw_data:  Raw data of the dataset
		:param parent:  Parent of this widget
		"""
		QtGui.QWidget.__init__(self, parent)
		self.dataset_raw_data = dataset_raw_data

		## GUI creation
		self.top_layer_widget = QtGui.QWidget()

		# Dataset children display
		self.children_tree = QtGui.QTreeWidget()
		self.children_tree.setColumnCount(1)
		self.children_tree.setHeaderHidden(True)

		# Dataset content display
		self.content_tree = QtGui.QTreeWidget()
		self.content_tree.setColumnCount(3)
		header_item = QtGui.QTreeWidgetItem()
		header_item.setText(0, "Annotator")
		header_item.setText(1, "Metadata type")
		header_item.setText(2, "Is total ?")
		self.content_tree.setHeaderItem(header_item)

		self.top_hlayout = QtGui.QHBoxLayout(self)
		self.top_hlayout.addWidget(self.children_tree)
		self.top_hlayout.addWidget(self.content_tree)
		self.top_layer_widget.setLayout(self.top_hlayout)

		# Re-examination button
		self.scan_button = QtGui.QPushButton(self)
		self.scan_button.setText("Refresh content")
		self.scan_button.clicked.connect(self._refreshDataset)

		self.main_vlayout = QtGui.QVBoxLayout(self)
		self.main_vlayout.addWidget(self.top_layer_widget)
		self.main_vlayout.addWidget(self.scan_button)
		self.setLayout(self.main_vlayout)


		self._refresh_gui()

	def _refresh_gui(self):

		self.children_tree.clear()

		for child in self.dataset_raw_data[0]:
			item = QtGui.QTreeWidgetItem()
			self.children_tree.addTopLevelItem(item)
			item.setText(0, str(child))

		self.children_tree.resizeColumnToContents(0)
		self.children_tree.update()

		# Here we are about to provide ways to change the dataset's content
		# It is directly connected to the file content so this organization
		# breaks the MVC pattern.. However it is unusual in our use cases to
		# modify the raw_data of a QiDataObject, so the only three options were
		# - break the MVC pattern by having the View modifying the Model directly
		# - have a signal at every level to relay the information
		# - have a connection from the controller directly to here through each layer
		# The second option would break the genericity of the upper layer, or force all
		# other widgets to have a signal they would not use.
		# The third option would be very sensitive to API change and therefore be slightly
		# harder to maintain.
		# As a result, I decided to go for the first option
		content = self.dataset_raw_data[1].toDict()["metadata_info"]

		self.content_tree.clear()

		for annotator in content:
			for metadata_type in content[annotator]:
				item = QtGui.QTreeWidgetItem()
				self.content_tree.addTopLevelItem(item)
				item.setText(0, str(annotator))
				item.setText(1, str(metadata_type))

				inputWidget = QtGui.QCheckBox(self)
				inputWidget.setCheckState(QtCore.Qt.Checked if content[annotator][metadata_type] else QtCore.Qt.Unchecked)
				inputWidget.stateChanged.connect(
				    lambda x: self.dataset_raw_data[1].setMetadataTotalityStatus(
				        annotator,
				        metadata_type,
				        (x == QtCore.Qt.Checked)
				    )
				)
				self.content_tree.setItemWidget(item, 2, inputWidget)

		self.content_tree.resizeColumnToContents(0)
		self.content_tree.update()

	# ───────
	# Methods

	def addObject(self, coordinates):
		"""
		Add a metadata object to display on the view.

		:param coordinates:  Coordinates of the object to show (format depends on data type)
		:return:  Reference to the widget representing the object

		.. note::
			The returned reference is handy to connect callbacks on the
			widget signals. This reference is also needed to remove the object.
		"""
		# This won't be called for now, as it deals with localized metadata
		r = MetadataBaseItem()
		return r

	def removeItem(self, item):
		"""
		Remove an object from the widget

		:param item:  Reference to the widget
		"""
		return

	# ───────────────
	# Private methods

	def _refreshDataset(self):
		self.parent().displayed_object.examineContent()
		self.dataset_raw_data = self.parent().displayed_object.raw_data
		self._refresh_gui()
