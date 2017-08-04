
# Third-party libraries
import cv2
from PySide import QtCore, QtGui
import pytest

# Local modules
from qidata_gui._subwidgets import (
                                    SelectableListWidget,
                                    TickableListWidget,
                                   )
from qidata_gui._subwidgets.raw_data_display_widgets import RawDataDisplayWidget

def test_ticking_list_widget(qtbot):
	widget = TickableListWidget(["jdoe", "jsmith"])

	# Check items state
	ref1 = QtCore.Qt.ItemIsSelectable\
	       | QtCore.Qt.ItemIsUserCheckable\
	       | QtCore.Qt.ItemIsEnabled
	assert(ref1 == widget.item(0).flags())
	assert(ref1 == widget.item(1).flags())
	assert(QtCore.Qt.Checked == widget.item(0).checkState())
	assert(QtCore.Qt.Checked == widget.item(1).checkState())

	# Create list of one tickable and two always ticked elements
	widget = TickableListWidget(["jsmith"], ["jdoe", "jbond"])
	ref2 = QtCore.Qt.ItemIsSelectable\
	       | QtCore.Qt.ItemIsUserCheckable
	assert(ref2 == widget.item(0).flags())
	assert(ref2 == widget.item(1).flags())
	assert(ref1 == widget.item(2).flags())

	widget = TickableListWidget(["jdoe", "jsmith", "jbond"])
	qtbot.addWidget(widget)

	with qtbot.waitSignal(widget.tickedSelectionChanged, timeout=500) as _s:
		widget.item(2).setCheckState(QtCore.Qt.Unchecked)
	assert(len(_s.args) == 1)
	assert(["jdoe", "jsmith"] == _s.args[0])

def test_selectable_list_widget(qtbot):
	widget = SelectableListWidget()
	i1 = widget.addItem("Hello")
	i2 = widget.addItem("World", "tr")
	qtbot.addWidget(widget)

	# Signal is raised when an item is clicked and its
	# value is returned
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		rect2 = widget.visualItemRect(i2)
		qtbot.mouseClick(widget.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 rect2.center())
	assert("tr" == _s.args[0])

	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		rect1 = widget.visualItemRect(i1)
		qtbot.mouseClick(widget.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 rect1.center())
	assert("Hello" == _s.args[0])

	# Clicking a second time on the same item does not emit a signal
	with qtbot.assertNotEmitted(widget.itemSelected):
		rect1 = widget.visualItemRect(i1)
		qtbot.mouseClick(widget.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 rect1.center())

	# But if item was deselected
	widget.deselectAll()
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		rect1 = widget.visualItemRect(i1)
		qtbot.mouseClick(widget.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 rect1.center())
	assert("Hello" == _s.args[0])

	# Clear all items and make sure none is left
	widget.clearAllItems()
	assert(None == widget.currentItem())
	assert(0 == widget.count())

	# Once an object is removed, clicking on it does not
	# trigger any signal
	with qtbot.assertNotEmitted(widget.itemSelected):
		qtbot.mouseClick(widget.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 rect2.center())

def test_raw_data_display_widget(qtbot, jpg_file_path):

	# Test raw data widget with wrong given type
	with pytest.raises(TypeError) as e:
		widget = RawDataDisplayWidget(None, "TYPE", cv2.imread(jpg_file_path))
	assert("No widget available for type TYPE" == e.value.message)

	# Create widget
	widget = RawDataDisplayWidget(None, "IMAGE", cv2.imread(jpg_file_path))

	assert("IMAGE" == widget.type_selector.currentText())

	# Add two items on the view
	i1=widget.addItem([[-10,-10],[20,20]], dict(key="value"))
	i2=widget.addItem([[100,100],[200,200]], dict(name="definition"))

	qtbot.addWidget(widget)
	widget.show()

	# Variable for convenience
	_view = widget._widget.view

	# Click on the view to select an object
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
	assert(dict(name="definition") == _s.args[0])

	# Clicking a second time on the same item does not emit a signal
	with qtbot.assertNotEmitted(widget.itemSelected):
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))

	# But if item was deselected
	widget.deselectAll()
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(
		                     QtCore.QPointF(110,180)
		                 ))
	assert(dict(name="definition") == _s.args[0])

	## Test the resizing of the scene
	# Click on the "fit window" button
	qtbot.mouseClick(widget._widget.fit_button, QtCore.Qt.LeftButton)

	# Make sure all the scene is visible
	scene_visible_part = _view.mapToScene(
	                         _view.viewport().geometry()
	                     ).boundingRect()
	assert(scene_visible_part.width() >= _view.scene().sceneRect().width())
	assert(scene_visible_part.height() >= _view.scene().sceneRect().height())

	# Click on the view to select a different object
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(-8,-8)))
	assert(dict(key="value") == _s.args[0])

	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		widget.selectItem(i2)
	assert(dict(name="definition") == _s.args[0])

	# Click on the "full size" button
	qtbot.mouseClick(widget._widget.full_button, QtCore.Qt.LeftButton)

	# Make sure now any visible section has the same size on the widget and in
	# the scene
	some_rect = _view.mapToScene(QtCore.QRect(0,0,150,100)).boundingRect()
	assert(150 == some_rect.width())
	assert(100 == some_rect.height())

	widget.clearAllItems()
	assert(1 == len(_view.scene().items()))
