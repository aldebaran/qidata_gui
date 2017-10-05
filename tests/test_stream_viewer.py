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
from pytestqt.exceptions import TimeoutError
import qidata

# Local modules
from qidata_gui._subwidgets import StreamViewer

def test_stream_viewer(qtbot, big_dataset_path):

	# Create widget in read-only
	with qidata.QiDataSet(big_dataset_path, "r") as _ds:
		_streams = _ds.getAllStreams()
		widget = StreamViewer(_streams)
		qtbot.addWidget(widget)
		widget.show()
		qtbot.waitUntil(widget.isVisible, 100)
		qtbot.wait(500) # Make SURE the widget is visible

		# Click on timeline on the last column of the grid
		first_grid_column = widget._timeline._history_left
		last_grid_column = widget._timeline._history_left + widget._timeline._history_width
		point_clicked = QtCore.QPoint(last_grid_column-1,40)
		point_clicked_in_scene = widget._timeline.mapToScene(point_clicked)
		point_clicked_in_view = widget.view.mapFromScene(point_clicked_in_scene)
		with qtbot.waitSignal(widget.objectSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.view.viewport(),
			                 QtCore.Qt.LeftButton,
			                 0,
			                 point_clicked_in_view
			                )
		assert(
		    "ir_51.png" == _s.args[0]
		)

		# Click next button => no signal
		with qtbot.assertNotEmitted(widget.objectSelected):
			qtbot.mouseClick(widget.next_button, QtCore.Qt.LeftButton)

		# Click previous button => signal
		with qtbot.waitSignal(widget.objectSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.previous_button, QtCore.Qt.LeftButton)

		assert(
		    "ir_50.png" == _s.args[0]
		)

		point_clicked = QtCore.QPoint(first_grid_column,40)
		point_clicked_in_scene = widget._timeline.mapToScene(point_clicked)
		point_clicked_in_view = widget.view.mapFromScene(point_clicked_in_scene)
		with qtbot.waitSignal(widget.objectSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.view.viewport(),
			                 QtCore.Qt.LeftButton,
			                 0,
			                 point_clicked_in_view
			                )
		assert(
		    "depth_00.png" == _s.args[0]
		)
		# Click previous button => no signal
		with qtbot.assertNotEmitted(widget.objectSelected):
			qtbot.mouseClick(widget.previous_button, QtCore.Qt.LeftButton)

		# Click next button => signal
		with qtbot.waitSignal(widget.objectSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.next_button, QtCore.Qt.LeftButton)

		assert(
		    "ir_00.png" == _s.args[0]
		)

		# Check that each "next" only change one file
		# This is not mandatory but quite usual in streams, as a frame is
		# created for each set of files, and it is rare that two files change
		# at the exact same timestamp
		previous_file = "ir_00.png"

		while True:
			try:
				with qtbot.waitSignal(widget.objectSelected, timeout=500) as _s:
					qtbot.mouseClick(widget.next_button, QtCore.Qt.LeftButton)
			except TimeoutError:
				# End of timeline was reached
				break

			assert(previous_file != _s.args[0])
			previous_set = _s.args[0]
