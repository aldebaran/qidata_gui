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
from PySide.QtCore import Qt
import qidata
from qidata.metadata_objects import Property, Object

# Local modules
from qidata_gui._subwidgets import (
                                    SelectableListWidget,
                                    TickableListWidget,
                                   )
from qidata_gui import QiDataSetWidget

def test_qidataset_widget(mock, qtbot, small_dataset_path):

	# Create widget in read-only
	with qidata.QiDataSet(small_dataset_path, "w") as _ds:
		widget = QiDataSetWidget(_ds)
		widget.show()
		qtbot.addWidget(widget)

		with _ds.openChild(_ds.children[0]) as _f:
			_f.addAnnotation("jdoe", Property(), None)

		assert(0 == widget.content_tree.topLevelItemCount())
		qtbot.mouseClick(widget.refresh_button, Qt.LeftButton)
		assert(1 == widget.content_tree.topLevelItemCount())
		item = widget.content_tree.topLevelItem(0)
		assert("jdoe" == item.text(0))
		assert("Property" == item.text(1))
		assert(
		    Qt.Unchecked == widget.content_tree.itemWidget(item,2).checkState()
		)
		widget.content_tree.itemWidget(item,2).setCheckState(Qt.Checked)
		widget.close()

	with qidata.QiDataSet(small_dataset_path) as _ds:
		widget = QiDataSetWidget(_ds)
		widget.show()
		qtbot.addWidget(widget)
		assert(1 == widget.content_tree.topLevelItemCount())
		item = widget.content_tree.topLevelItem(0)
		assert(
		    Qt.Checked == widget.content_tree.itemWidget(item,2).checkState()
		)
		widget.close()

	with qidata.QiDataSet(small_dataset_path, "w") as _ds:
		widget = QiDataSetWidget(_ds)
		widget.show()
		qtbot.addWidget(widget)

		_g = mock.patch.object(QtGui.QFileDialog,
		                       'getOpenFileNames',
		                       return_value=([],""))
		_c = mock.patch.object(QtGui.QMessageBox,
		                       'critical',
		                       return_value=QtGui.QMessageBox.Ok)
		qtbot.mouseClick(widget.plus_button, Qt.LeftButton)
		assert(not _c.called)

		_g = mock.patch.object(QtGui.QFileDialog,
		                       'getOpenFileNames',
		                       return_value=(["depth_00.png"],""))
		_c = mock.patch.object(QtGui.QMessageBox,
		                       'critical',
		                       return_value=QtGui.QMessageBox.Ok)
		qtbot.mouseClick(widget.plus_button, Qt.LeftButton)
		assert(_c.called)

		_c.reset_mock()
		mock.patch.object(
		                      QtGui.QFileDialog,
		                      'getOpenFileNames',
		                      return_value=(
		                          [
		                              "depth_00.png",
		                              "front_00.png",
		                              "ir_00.png"
		                          ],
		                          ""
		                      )
		                 )
		qtbot.mouseClick(widget.plus_button, Qt.LeftButton)
		assert(not _c.called)

def test_qidataset_frame_no_tf(mock, qtbot, dataset_with_frame_path):
	with qidata.QiDataSet(dataset_with_frame_path, "w") as _ds:
		widget = QiDataSetWidget(_ds)
		widget.show()
		qtbot.addWidget(widget)
		assert(not widget._has_streams)

		top_item = widget.frames_list.topLevelItem(0)
		rect = widget.frames_list.visualItemRect(top_item)

		# Select the frame
		qtbot.mouseClick(widget.frames_list.viewport(),
		                  QtCore.Qt.LeftButton,
		                  0,
		                  rect.center())
		assert(widget.minus_button.isEnabled())

		# Item activation cannot be simulated by a mouse click so we have to
		# manually send the signal..
		widget.frames_list.itemActivated.emit(
		    widget.frames_list.topLevelItem(0),
		    0
		)

		# Frame should now be displayed, remove it
		qtbot.mouseClick(widget.minus_button, QtCore.Qt.LeftButton)
		qtbot.wait(100)
		assert(0 == widget.frames_list.topLevelItemCount())

def test_qidataset_stream(mock, qtbot, big_dataset_path):
	with qidata.QiDataSet(big_dataset_path, "w") as _ds:
		widget = QiDataSetWidget(_ds)
		widget.show()
		qtbot.addWidget(widget)
		assert(widget._has_streams)
