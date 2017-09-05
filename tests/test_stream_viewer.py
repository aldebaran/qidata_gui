

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
		with qtbot.waitSignal(widget.frameSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.view.viewport(),
			                 QtCore.Qt.LeftButton,
			                 0,
			                 point_clicked_in_view
			                )
		assert(
		    set([
		        "depth_51.png",
		        "front_39.png",
		        "ir_51.png"
		    ]) == set(_s.args[0])
		)

		# Click next button => no signal
		with qtbot.assertNotEmitted(widget.frameSelected):
			qtbot.mouseClick(widget.next_button, QtCore.Qt.LeftButton)

		# Click previous button => signal
		with qtbot.waitSignal(widget.frameSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.previous_button, QtCore.Qt.LeftButton)

		assert(
		    set([
		        "depth_51.png",
		        "front_39.png",
		        "ir_50.png"
		    ]) == set(_s.args[0])
		)

		point_clicked = QtCore.QPoint(first_grid_column,40)
		point_clicked_in_scene = widget._timeline.mapToScene(point_clicked)
		point_clicked_in_view = widget.view.mapFromScene(point_clicked_in_scene)
		with qtbot.waitSignal(widget.frameSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.view.viewport(),
			                 QtCore.Qt.LeftButton,
			                 0,
			                 point_clicked_in_view
			                )
		assert(
		    set([
		        "depth_00.png",
		    ]) == set(_s.args[0])
		)
		# Click previous button => no signal
		with qtbot.assertNotEmitted(widget.frameSelected):
			qtbot.mouseClick(widget.previous_button, QtCore.Qt.LeftButton)

		# Click next button => signal
		with qtbot.waitSignal(widget.frameSelected, timeout=500) as _s:
			qtbot.mouseClick(widget.next_button, QtCore.Qt.LeftButton)

		assert(
		    set([
		        "depth_01.png",
		        "front_00.png",
		        "ir_00.png"
		    ]) == set(_s.args[0])
		)

		# Check that each "next" only change one file
		# This is not mandatory but quite usual in streams, as a frame is
		# created for each set of files, and it is rare that two files change
		# at the exact same timestamp
		previous_set = set([
		        "depth_01.png",
		        "front_00.png",
		        "ir_00.png"
		    ])

		while True:
			try:
				with qtbot.waitSignal(widget.frameSelected, timeout=500) as _s:
					qtbot.mouseClick(widget.next_button, QtCore.Qt.LeftButton)
			except TimeoutError:
				# End of timeline was reached
				break

			assert(2 == len(previous_set.intersection(set(_s.args[0]))))
			previous_set = set(_s.args[0])
