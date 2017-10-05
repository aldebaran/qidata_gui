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
from PySide import QtCore, QtGui
import qidata
from qidata.metadata_objects import Property, Object

# Local modules
from qidata_gui import QiDataFrameWidget

def test_qidataframe_widget_read_only(qtbot, dataset_with_frame_path):

	# Create widget in read-only
	with qidata.QiDataSet(dataset_with_frame_path, "r") as _ds:
		frame_0 = _ds.getAllFrames()[0]
		widget = QiDataFrameWidget(_ds, frame_0)
		widget.show()
		qtbot.addWidget(widget)

		assert(widget.read_only)
		assert(not widget.minus_button.isEnabled())
		assert(not widget.plus_button.isEnabled())
		assert(not widget.type_selector.isEnabled())
		assert(widget.frame_viewer.read_only)
		assert(widget.annotation_displayer.read_only)

def test_qidataframe_widget_addition(qtbot, mock, dataset_with_frame_path, dataset_with_frame_and_tf_path):

	# Create widget in "w" mode
	with qidata.QiDataSet(dataset_with_frame_path, "w") as _ds:
		frame_0 = _ds.getAllFrames()[0]
		widget = QiDataFrameWidget(_ds, frame_0, "jsmith")

		widget.show()
		qtbot.addWidget(widget)

		assert(not widget.read_only)
		assert(not widget.minus_button.isEnabled())
		assert(widget.plus_button.isEnabled())
		assert(not widget.type_selector.isEnabled())
		assert(not widget.frame_viewer.read_only)
		assert(not widget.annotation_displayer.read_only)

		# Create a new global annotation
		qtbot.mouseClick(widget.plus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)

		# Select unlocalized annotation
		qtbot.mouseClick(widget.global_annotation_displayer.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 QtCore.QPoint(10,10)
		                )
		qtbot.wait(100)
		assert(widget.minus_button.isEnabled())
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

		assert(
		    [
		        Object(type="qrcode", value="", id=0),
		        None
		    ] == frame_0.annotations["jsmith"]["Object"][0]
		)
		widget.close()

	with qidata.QiDataSet(dataset_with_frame_path, "w") as _ds:
		frame_0 = _ds.getAllFrames()[0]
		assert(
		    [
		        Object(type="qrcode", value="", id=0),
		        None
		    ] == frame_0.annotations["jsmith"]["Object"][0]
		)

		widget = QiDataFrameWidget(_ds, frame_0, "jsmith")
		widget.show()
		qtbot.addWidget(widget)

		# Select the annotation we created and delete it
		qtbot.mouseClick(widget.global_annotation_displayer.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 QtCore.QPoint(10,10)
		                )

		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		qtbot.mouseClick(widget.minus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)
		assert(not widget.minus_button.isEnabled())
		assert(not frame_0.annotations.has_key("jsmith"))

		widget.close()

	# Create widget in "w" mode
	with qidata.QiDataSet(dataset_with_frame_and_tf_path, "w") as _ds:
		frame_0 = _ds.getAllFrames()[0]
		widget = QiDataFrameWidget(_ds, frame_0, "jsmith")
		widget.show()
		qtbot.addWidget(widget)

		# Create a new localized annotation
		qtbot.mouseClick(widget.frame_viewer.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.frame_viewer.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 )
		                )
		qtbot.wait(100)

		# And select it
		qtbot.mouseClick(widget.frame_viewer.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.frame_viewer.view.mapFromScene(
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

		# Add another object within a different view
		qtbot.mouseClick(widget.frame_viewer.xz_button, QtCore.Qt.LeftButton)

		qtbot.mouseClick(widget.frame_viewer.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.frame_viewer.view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 )
		                )
		qtbot.wait(100)

		# Add a third object that will be deleted
		qtbot.mouseClick(widget.frame_viewer.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.frame_viewer.view.mapFromScene(
		                     QtCore.QPointF(400,0)
		                 )
		                )
		qtbot.wait(100)

		# Select it
		qtbot.mouseClick(widget.frame_viewer.view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 widget.frame_viewer.view.mapFromScene(
		                     QtCore.QPointF(400,0)
		                 )
		                )
		qtbot.wait(100)

		# Ask for deletion and say yes
		mock.patch.object(QtGui.QMessageBox,
		                  'warning',
		                  return_value=QtGui.QMessageBox.Yes)
		qtbot.mouseClick(widget.frame_viewer.view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 widget.frame_viewer.view.mapFromScene(
		                     QtCore.QPointF(400,0)
		                 )
		                )
		qtbot.wait(100)
		widget.close()

	with qidata.QiDataSet(dataset_with_frame_and_tf_path, "w") as _ds:
		_f = _ds.getAllFrames()[0]

		assert(
		    [
		        Object(type="qrcode", value="", id=0),
		        [[-0.3,-1.4,-2.1],[0.3,-0.8,-1.5]]
		    ] == _f.annotations["jsmith"]["Object"][0]
		)

		assert(
		    [
		        Object(type="", value="", id=0),
		        [[0.8,-0.3,-2.1],[1.4,0.3,-1.5]]
		    ] == _f.annotations["jsmith"]["Object"][1]
		)

		assert(2 == len(_f.annotations["jsmith"]["Object"]))