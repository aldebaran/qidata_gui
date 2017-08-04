# -*- coding: utf-8 -*-

# Third-party libraries
from PySide import QtGui, QtCore
from qidata import DataType

# Local modules
from .image_widget import ImageWidget

# ────────────
# Data Widgets

SUPPORTED_WIDGETS = {
	"IMAGE": ImageWidget,
	"IMAGE_2D": ImageWidget,
	"IMAGE_3D": ImageWidget,
	"IMAGE_IR": ImageWidget,
}

def makeRawDataWidget(parent_widget, data_type, raw_data):
	"""
	Create relevant widget for required data type.
	:param parent_widget: Parent of this widget
	:type parent_widget: PySide.QtGui.QWidget
	:param qidata_sensor_object: Object to display
	:type qidata_sensor_object: qidata.qidata_sensor_object.QiDataSensorObject
	:return: Widget displaying the raw data of the object
	:rtype: qidata_gui._subwidgets.raw_data_display.RawDataDisplayInterface
	:raise: TypeError if given type name is unknown
	"""
	try:
		_w = SUPPORTED_WIDGETS[str(data_type)]
		return _w(raw_data, parent_widget)
	except KeyError:
		msg = "No widget available for type %s"%data_type
		raise TypeError(msg)

class RawDataDisplayWidget(QtGui.QWidget):

	itemSelected = QtCore.Signal(list)

	def __init__(self, parent_widget, data_type, raw_data):
		super(RawDataDisplayWidget, self).__init__(parent_widget)

		## Header
		self.top_widget = QtGui.QWidget(self)

		# Image type selector
		self.type_selector = QtGui.QComboBox()
		self.type_selector.setEnabled(False)
		self.type_selector.addItems(
		    map(str, list(DataType))
		)
		self.type_selector.setCurrentIndex(
		    self.type_selector.findText(str(data_type))
		)

		# Aggregation
		self.top_layout = QtGui.QHBoxLayout(self)
		self.top_layout.addWidget(self.type_selector)
		self.top_widget.setLayout(self.top_layout)

		# Create widget, assign it the parent and the object
		self._widget = makeRawDataWidget(self, data_type, raw_data)
		self._widget.itemSelected.connect(self.itemSelected)

		self.main_hlayout = QtGui.QVBoxLayout(self)
		self.main_hlayout.addWidget(self.top_widget)
		self.main_hlayout.addWidget(self._widget)
		self.setLayout(self.main_hlayout)

	# ──────────
	# Public API

	def addItem(self, location, info):
		"""
		Add a item to display on the view.

		:param location: Coordinates of the item to show (depends on data type)
		:param info: The info represented by the item
		:return:  Reference to the widget representing the object

		.. note::
			The returned reference is handy to connect callbacks on the
			widget signals. This reference is also needed to remove the object.
		"""
		return self._widget.addItem(location, info)

	def selectItem(self, item):
		"""
		Give the focus to an item, and de-focus any previously selected item
		"""
		self._widget.selectItem(item)

	def deselectAll(self):
		"""
		De-focus any focused item
		"""
		self._widget.focusOutSelectedItem()

	def clearAllItems(self):
		"""
		Remove all items from the widget
		"""
		self._widget.clearAllItems()
