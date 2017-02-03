# -*- coding: utf-8 -*-

# Qt
from PySide.QtGui import QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QCheckBox
from PySide.QtCore import Signal, Qt

class DataSetWidget(QWidget):
	"""
	Widget specialized in displaying audio with Metadata Objects
	"""

	# ───────
	# Signals

	objectAdditionRequired = Signal(list)

	# ───────────
	# Constructor

	def __init__(self, dataset_content, parent=None):
		"""
		DataSetWidget constructor

		:param dataset_content:  Raw data of the dataset
		:param parent:  Parent of this widget
		"""
		QWidget.__init__(self, parent)

		## GUI creation
		# Dataset children display
		self.children_tree = QTreeWidget()
		self.children_tree.setColumnCount(1)
		self.children_tree.setHeaderHidden(True)

		for child in dataset_content[0]:
			item = QTreeWidgetItem()
			self.children_tree.addTopLevelItem(item)
			item.setText(0, str(child))

		self.children_tree.resizeColumnToContents(0)

		# Dataset content display
		self.content_tree = QTreeWidget()
		self.content_tree.setColumnCount(3)
		header_item = QTreeWidgetItem()
		header_item.setText(0, "Annotator")
		header_item.setText(1, "Metadata type")
		header_item.setText(2, "Is total ?")
		self.content_tree.setHeaderItem(header_item)

		content = dataset_content[1].toDict()["metadata_info"]

		for annotator in content:
			for metadata_type in content[annotator]:
				item = QTreeWidgetItem()
				self.content_tree.addTopLevelItem(item)
				item.setText(0, str(annotator))
				item.setText(1, str(metadata_type))

				# Here we provided a way to change the dataset's annotation status
				# It is directly connected to the file content so this organization
				# breaks the MVC pattern.. However it is unusual in our use cases to
				# modify the raw_data of a QiDataObject, so this is the only way to
				# avoid either useless signals at every level or a connection through
				# multiple layer. The second option would probably be the best choice,
				# but I'd rather use the current one, which is easier to maintain.
				inputWidget = QCheckBox(self)
				inputWidget.setCheckState(Qt.Checked if content[annotator][metadata_type] else Qt.Unchecked)
				inputWidget.stateChanged.connect(
				    lambda x: dataset_content[1].setMetadataTotalityStatus(
				        annotator,
				        metadata_type,
				        (x == Qt.Checked)
				    )
				)
				self.content_tree.setItemWidget(item, 2, inputWidget)

		self.content_tree.resizeColumnToContents(0)

		self.main_hlayout = QHBoxLayout(self)
		self.main_hlayout.addWidget(self.children_tree)
		self.main_hlayout.addWidget(self.content_tree)
		self.setLayout(self.main_hlayout)

		## Mettre un bouton ici pour refresh le contenu du dataset ?

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