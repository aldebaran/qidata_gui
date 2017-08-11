# -*- coding: utf-8 -*-

# Standard libraries
import argparse
import sys

# Third-party libraries
from qidata import DataType
from qidata.metadata_objects import Context
from PySide import QtCore, QtGui
from strong_typing import ObjectDisplayWidget

try:
	from rosbag import Bag as RosBag
	_has_ros = True
except ImportError:
	_has_ros = False

# Local modules
from qidata_apps import QiDataApp
from lib import makeQiDataSetFromROSbag

if _has_ros:

	class MainWidget(QtGui.QWidget):

		# ───────
		# Signals

		elementSkipped = QtCore.Signal()
		inputValidated = QtCore.Signal()

		# ───────────
		# Constructor

		def __init__(self):
			"""
			Construct the widget to define how to transform the ROSbag in a
			DataSet
			"""
			QtGui.QWidget.__init__(self)
			self.main_hlayout = QtGui.QHBoxLayout(self)
			self.setLayout(self.main_hlayout)

			# ────────────
			# GUI creation

			self.left_widget = QtGui.QWidget(self)
			self.left_vlayout = QtGui.QVBoxLayout(self.left_widget)
			self.main_hlayout.addWidget(self.left_widget)

			self.right_widget = ObjectDisplayWidget(self)
			self.right_widget.data = Context()
			self.main_hlayout.addWidget(self.right_widget)

			# Topic listing widget
			self.content_tree = QtGui.QTreeWidget()
			self.left_vlayout.addWidget(self.content_tree)
			self.content_tree.setColumnCount(3)
			header_item = QtGui.QTreeWidgetItem()
			header_item.setText(0, "Topic")
			header_item.setText(1, "Name")
			header_item.setText(2, "DataType")
			self.content_tree.setHeaderItem(header_item)

			# Buttons bar
			self.buttons = QtGui.QWidget()
			self.button_hlayout = QtGui.QHBoxLayout(self.buttons)
			self.buttons.setLayout(self.button_hlayout)
			self.left_vlayout.addWidget(self.buttons)

			self.ok_button = QtGui.QPushButton(self)
			self.ok_button.setText("OK")
			self.ok_button.clicked.connect(self.inputValidated)
			self.button_hlayout.addWidget(self.ok_button)

			self.skip_button = QtGui.QPushButton(self)
			self.skip_button.setText("Skip")
			self.skip_button.clicked.connect(self.elementSkipped)
			self.button_hlayout.addWidget(self.skip_button)

			# Restore saved geometry
			settings = QtCore.QSettings("Softbank Robotics", "ROSbagConverter")
			self.restoreGeometry(settings.value("geometry"))


		# ──────────
		# Public API

		def populate(self, topic_list):
			"""
			Fill the main widget with the topics retrieved from the ROSbag

			:param topic_list: List of topics to display
			:param topic_list: list
			"""
			self.content_tree.clear()
			type_list = map(str, list(DataType))
			type_list.sort()

			for topic in topic_list:
				item = QtGui.QTreeWidgetItem()
				self.content_tree.addTopLevelItem(item)
				item.setText(0, str(topic))

				nameWidget = QtGui.QLineEdit(self)
				nameWidget.setSizePolicy(QtGui.QSizePolicy.Expanding,
				                         QtGui.QSizePolicy.Fixed)
				self.content_tree.setItemWidget(item, 1, nameWidget)

				typeWidget = QtGui.QComboBox(self)
				typeWidget.setSizePolicy(QtGui.QSizePolicy.Fixed,
				                         QtGui.QSizePolicy.Fixed)
				typeWidget.addItems(type_list)
				self.content_tree.setItemWidget(item, 2, typeWidget)

			self.content_tree.resizeColumnToContents(0)
			self.content_tree.update()

		def getInputs(self):
			"""
			Returns the values given by the user

			:return: Map of topic name to stream name and data type
			:rtype: dict
			"""
			out = dict()
			for i in range(0, self.content_tree.topLevelItemCount()):
				item = self.content_tree.topLevelItem(i)
				topic = item.text(0)
				name = self.content_tree.itemWidget(item, 1).text()
				datatype = self.content_tree.itemWidget(item, 2).currentText()
				out[str(topic)] = (str(name), DataType[str(datatype)])
			return out

		# ─────
		# Slots

		def closeEvent(self, event):
			settings = QtCore.QSettings("Softbank Robotics", "ROSbagConverter")
			settings.setValue("geometry", self.saveGeometry())
			QtGui.QWidget.closeEvent(self, event)
			return True

	class App(QiDataApp):

		# ───────────
		# Constructor

		def __init__(self, rosbag_list):
			self.rosbag_iter = iter(rosbag_list)

			QiDataApp.__init__(self, "QiDataSet maker")
			self.main_window.main_widget = MainWidget()
			self.main_window.main_widget.inputValidated.connect(self._processInputs)
			self.main_window.main_widget.elementSkipped.connect(self._showNextBag)
			self.current_bag = None
			self._showNextBag()

		# ───────────
		# Private API

		def _processInputs(self):
			# Take given inputs and convert the bag
			inputs = self.main_window.main_widget.getInputs()
			context = self.main_window.main_widget.right_widget.data
			for topic in inputs.keys():
				if inputs[topic][0] == "":
					inputs.pop(topic)
			makeQiDataSetFromROSbag(self.current_bag, inputs, context)

			# Display the next bag to process
			self._showNextBag()

		def _showNextBag(self):
			# Display the next bag details if there is one
			try:
				self.current_bag = self.rosbag_iter.next()
			except StopIteration:
				self.main_window.close()
			else:
				self.main_window.setWindowTitle(self.current_bag)
				with RosBag(self.current_bag, "r") as bag:
					tl = bag.get_type_and_topic_info()[1]
					if tl.has_key("/tf"):
						tl.pop("/tf")
				self.main_window.main_widget.populate(tl.keys())

	def main(args):
		qidata_app = App(args.rosbag_path)
		try:
			qidata_app.run()
		except KeyboardInterrupt:
			pass

else:
	def main(args):
		print "No ROS workspace was found. Source a ROS workspace and try again"

# ─────────────────────────────
# Definitions for Qidata plugin

DESCRIPTION = "Creates a QiDataSet from a ROSbag"

if not _has_ros:
	DESCRIPTION += " [UNAVAILABLE. Try to source a ROS workspace]"

def make_command_parser(parser=argparse.ArgumentParser(description=DESCRIPTION)):
	rosbag_arg = parser.add_argument("rosbag_path",
	                                 nargs="+",
	                                 help="ROSbag to convert in QiDataSet",
	                                 default="*.bag"
	                                )
	parser.set_defaults(func=main)
	return parser

# ───────────────────
# Add a main launcher

if __name__ == "__main__":
	parser = make_command_parser()
	parsed_args = parser.parse_args(sys.argv[1:])
	parsed_args.func(parsed_args)
