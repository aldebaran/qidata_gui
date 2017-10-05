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

# Third-party libraries
import cv2
from PySide import QtCore, QtGui
import qidata
from qidata.metadata_objects import Property, Object

# Local modules
from qidata_gui._subwidgets import (
                                    SelectableListWidget,
                                    TickableListWidget,
                                   )
from qidata_gui import QiDataSensorWidget

def test_qidatasensor_widget_read_only(qtbot, mock, jpg_file_path):

	# Create widget in read-only
	with qidata.open(jpg_file_path) as _f:
		widget = QiDataSensorWidget(_f)
		widget.show()
		qtbot.addWidget(widget)

		assert(widget.read_only)
		assert(not widget.minus_button.isEnabled())
		assert(not widget.plus_button.isEnabled())
		assert(not widget.type_selector.isEnabled())
		assert(widget.timestamp_displayer.read_only)
		assert(widget.transform_displayer.read_only)
		assert(widget.raw_data_viewer.read_only)
		assert(widget.annotation_displayer.read_only)

		# Click on localized annotation
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)
		assert(
		    Property(key="key", value="value")==widget.annotation_displayer.data
		)
		assert("Property" == widget.type_selector.currentText())
		assert(not widget.type_selector.isEnabled())

		# Click on global annotation
		qtbot.mouseClick(widget.global_annotation_displayer.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 QtCore.QPoint(10,10)
		                )
		qtbot.wait(100)
		assert(
		    Property(
		        key="name",
		        value="definition"
		    ) == widget.annotation_displayer.data
		)
		assert(not widget.minus_button.isEnabled())

		widget.annotators_list.item(1).setCheckState(QtCore.Qt.Unchecked)
		assert(0 == len(widget.raw_data_viewer._widget.view.scene().items()))

		widget.annotators_list.item(0).setCheckState(QtCore.Qt.Unchecked)
		assert(0 == widget.global_annotation_displayer.count())

		# Make sure the "do you want to save box" does not show, as it is read
		# only
		mock.patch.object(QtGui.QMessageBox,
		                  'question',
		                  side_effect=Exception())
		widget.close()

def test_qidatasensor_widget_read_write_modify(qtbot, mock, jpg_file_path):

	# Create widget in "w" mode
	with qidata.open(jpg_file_path, "w") as _f:
		widget = QiDataSensorWidget(_f)
		widget.show()
		qtbot.addWidget(widget)

		assert(not widget.read_only)
		assert(not widget.minus_button.isEnabled())
		assert(not widget.plus_button.isEnabled())
		assert(not widget.type_selector.isEnabled())
		assert(not widget.timestamp_displayer.read_only)
		assert(not widget.transform_displayer.read_only)
		assert(not widget.raw_data_viewer.read_only)
		assert(not widget.annotation_displayer.read_only)

		# Select localized annotation
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)

		assert(widget.type_selector.isEnabled())

		# Change its type and cancel
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.No)
		widget.type_selector.setCurrentIndex(
		    widget.type_selector.findText("Object")
		)
		assert("Property" == widget.type_selector.currentText())

		# Change its type and validate
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		widget.type_selector.setCurrentIndex(
		    widget.type_selector.findText("Object")
		)
		assert("Object" == widget.type_selector.currentText())
		assert("Object" == type(widget.annotation_displayer.data).__name__)

		# And modify it
		item = widget.annotation_displayer.topLevelItem(0)
		w = widget.annotation_displayer.itemWidget(item,1)
		w.setText("qrcode")
		w.editingFinished.emit()

		# Select unlocalized annotation
		qtbot.mouseClick(widget.global_annotation_displayer.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 QtCore.QPoint(10,10)
		                )
		qtbot.wait(100)
		assert(widget.minus_button.isEnabled())

		# And delete it
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		qtbot.mouseClick(widget.minus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)

		# Badly change object type
		mock.patch.object(QtGui.QMessageBox,
		                  'critical',
		                  return_value=QtGui.QMessageBox.Ok)
		widget.raw_data_viewer.type_selector.setCurrentIndex(
		    widget.raw_data_viewer.type_selector.findText("AUDIO")
		)
		assert("IMAGE" == widget.raw_data_viewer.type_selector.currentText())
		assert("IMAGE" == str(_f.type))
		widget.raw_data_viewer.type_selector.setCurrentIndex(
		    widget.raw_data_viewer.type_selector.findText("IMAGE_2D")
		)
		assert("IMAGE_2D" == str(_f.type))

		mock.patch.object(QtGui.QMessageBox,
		                  'question',
		                  return_value=QtGui.QMessageBox.Yes)
		widget.close()

	with qidata.open(jpg_file_path) as _f:
		assert(
		    [
		        Object(type="qrcode", value="", id=0),
		        [[50,50],[650,590]]
		    ] == _f.annotations["jsmith"]["Object"][0]
		)
		assert(not _f.annotations.has_key("jdoe"))
		assert("IMAGE_2D" == str(_f.type))

def test_qidatasensor_widget_read_write_deletion(qtbot, mock, jpg_file_path):

	# Create widget in "w" mode
	with qidata.open(jpg_file_path, "w") as _f:
		widget = QiDataSensorWidget(_f)
		widget.show()
		qtbot.addWidget(widget)

		# Select localized annotation
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)

		# And ask for deletion but close
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Close)
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)
		assert(
		    [
		        Property(key="key", value="value"),
		        [[50,50],[650,590]]
		    ] == _f.annotations["jsmith"]["Property"][0]
		)

		# Ask for deletion but say no
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.No)
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)
		assert(
		    [
		        Property(key="key", value="value"),
		        [[50,50],[650,590]]
		    ] == _f.annotations["jsmith"]["Property"][0]
		)

		# Ask for deletion again and say yes
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)
		assert(
		    widget.annotation_displayer.data is None
		)
		assert(not widget.type_selector.isEnabled())

		mock.patch.object(QtGui.QMessageBox,
		                  'question',
		                  return_value=QtGui.QMessageBox.Yes)
		widget.close()

	with qidata.open(jpg_file_path) as _f:
		assert(
		    [
		        Property(key="name", value="definition"),
		        None
		    ] == _f.annotations["jdoe"]["Property"][0]
		)
		assert(not _f.annotations.has_key("jsmith"))

def test_qidatasensor_widget_read_write_addition(qtbot, mock, jpg_file_path):

	# Create widget in "w" mode
	with qidata.open(jpg_file_path, "w") as _f:
		widget = QiDataSensorWidget(_f, "jwayne")

		widget.show()
		qtbot.addWidget(widget)

		assert(not widget.read_only)
		assert(not widget.minus_button.isEnabled())
		assert(widget.plus_button.isEnabled())
		assert(not widget.type_selector.isEnabled())
		assert(not widget.timestamp_displayer.read_only)
		assert(not widget.transform_displayer.read_only)
		assert(not widget.raw_data_viewer.read_only)
		assert(not widget.annotation_displayer.read_only)

		# Then create a new localized annotation
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(1000,180)
		                 )
		                )
		qtbot.wait(100)

		# And a new global annotation
		qtbot.mouseClick(widget.plus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)

		mock.patch.object(QtGui.QMessageBox,
		                  'question',
		                  return_value=QtGui.QMessageBox.Yes)
		widget.close()

	with qidata.open(jpg_file_path) as _f:
		assert(
		    [
		        Property(key="", value=""),
		        [[970,150],[1030,210]]
		    ] == _f.annotations["jwayne"]["Property"][0]
		)
		assert(
		    [
		        Property(key="", value=""),
		        None
		    ] == _f.annotations["jwayne"]["Property"][1]
		)

def test_qidatasensor_widget_do_not_save(qtbot, mock, jpg_file_path):

	# Create widget in "w" mode
	with qidata.open(jpg_file_path, "w") as _f:
		widget = QiDataSensorWidget(_f, "sambrose")
		widget.show()
		qtbot.addWidget(widget)

		# Select localized annotation
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.raw_data_viewer._widget.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
		qtbot.wait(100)

		# Change its type and validate
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		widget.type_selector.setCurrentIndex(
		    widget.type_selector.findText("Object")
		)
		assert("Object" == widget.type_selector.currentText())
		assert("Object" == type(widget.annotation_displayer.data).__name__)

		# And modify it
		item = widget.annotation_displayer.topLevelItem(0)
		w = widget.annotation_displayer.itemWidget(item,1)
		w.setText("qrcode")
		w.editingFinished.emit()

		# Select unlocalized annotation
		qtbot.mouseClick(widget.global_annotation_displayer.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 QtCore.QPoint(10,10)
		                )
		qtbot.wait(100)
		assert(widget.minus_button.isEnabled())

		# And delete it
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		qtbot.mouseClick(widget.minus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)

		# Then create a new localized annotation
		qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 QtCore.QPoint(1000,180)
		                 )
		qtbot.wait(100)

		# And a new global annotation
		qtbot.mouseClick(widget.plus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)

		# Close and do not save
		mock.patch.object(QtGui.QMessageBox,
		                  'question',
		                  return_value=QtGui.QMessageBox.No)
		widget.close()

	with qidata.open(jpg_file_path) as _f:
		assert(
		    [
		        Property(key="name", value="definition"),
		        None
		    ] == _f.annotations["jdoe"]["Property"][0]
		)
		assert(
		    [
		        Property(key="key", value="value"),
		        [[50,50],[650,590]]
		    ] == _f.annotations["jsmith"]["Property"][0]
		)
		assert(not _f.annotations.has_key("sambrose"))
		assert("IMAGE" == str(_f.type))