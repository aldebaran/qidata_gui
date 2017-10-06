
# Standard libraries
import threading
import time

# Third-party libraries
import cv2
from image import Image
from PySide import QtCore, QtGui
from pymouse import PyMouse
import pytest

# Local modules
from qidata_gui._subwidgets import (
                                    SelectableListWidget,
                                    TickableListWidget,
                                   )
from qidata_gui._subwidgets.raw_data_display_widgets import RawDataDisplayWidget

def mouseDrag(qtbot, source, dest):
	"""
	Simulate a mouse drag from source to dest
	"""
	def drag(source, dest):
		mouse = PyMouse()
		mouse.move(*source)
		time.sleep(0.5)
		mouse.drag(*dest)

	dragThread = threading.Thread(
	                 target=drag,
	                 args=(
	                          source,
	                          dest
	                      )
	             )
	dragThread.start()
	while dragThread.is_alive():
		qtbot.wait(1000)

def mouseScroll(qtbot, vertical=None):
	"""
	Simulate a mouse scroll
	"""
	def scroll(vertical):
		mouse = PyMouse()
		time.sleep(0.5)
		mouse.scroll(vertical)

	scrollThread = threading.Thread(target=scroll,args=(vertical,))
	scrollThread.start()
	while scrollThread.is_alive():
		qtbot.wait(1000)

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

	# Selected item can be removed
	with qtbot.assertNotEmitted(widget.itemSelected):
		widget.removeSelectedItem()
	assert(None == widget.currentItem())
	assert(1 == widget.count())

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

	##########
	## NOTE ##
	##########

	# It seems that this test sometimes triggers the mouseMoveEvent although it
	# should not. So far, it did not cause any problem so I ignored it. But if
	# in the future some weird bug appears, it might be because events are
	# triggered randomly by the mouse simulation

	# Test raw data widget with wrong given type
	with pytest.raises(TypeError) as e:
		widget = RawDataDisplayWidget(None, "TYPE", Image(jpg_file_path))
	assert("No widget available for type TYPE" == e.value.message)

	# Create widget
	widget = RawDataDisplayWidget(None, "IMAGE", Image(jpg_file_path))
	qtbot.addWidget(widget)
	widget.show()
	assert("IMAGE" == widget.type_selector.currentText())

	# Variable for convenience
	_view = widget._widget.view

	# Add two items on the view
	i1=widget.addItem([[-10,-10],[20,20]], dict(key="value"))
	i2=widget.addItem([[100,100],[200,200]], dict(name="definition"))

	# Make sure all the scene is visible after clicking on the "fit window"
	# button
	qtbot.mouseClick(widget._widget.fit_button, QtCore.Qt.LeftButton)
	scene_visible_part = _view.mapToScene(
	                         _view.viewport().geometry()
	                     ).boundingRect()
	assert(scene_visible_part.width() >= _view.scene().sceneRect().width())
	assert(scene_visible_part.height() >= _view.scene().sceneRect().height())

	# Click on an object to select it
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(110,180))
		                )
	assert(dict(name="definition") == _s.args[0])
	assert(i2 == _view.scene()._selectedItem)

	# Clicking a second time on the same item does not emit a signal
	with qtbot.assertNotEmitted(widget.itemSelected):
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(110,180))
		                )

	# But if item was deselected, event is emitted again
	widget.deselectAll()
	assert(None == _view.scene()._selectedItem)
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(110,180))
		                )
	assert(dict(name="definition") == _s.args[0])

	# Click on a different object
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(-8,-8))
		                )
	assert(dict(key="value") == _s.args[0])
	assert(i1 == _view.scene()._selectedItem)

	# If an item is programmatically selected, event is also raised
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		widget.selectItem(i2)
	assert(dict(name="definition") == _s.args[0])

	# Make sure now any visible section has the same size on the widget and in
	# the scene after clicking the "full size" button
	qtbot.mouseClick(widget._widget.full_button, QtCore.Qt.LeftButton)
	some_rect = _view.mapToScene(QtCore.QRect(0,0,150,100)).boundingRect()
	assert(150 == some_rect.width())
	assert(100 == some_rect.height())

	# Remove the selected item and make sure it unselected it
	widget.removeItem(i2)
	assert(None == _view.scene()._selectedItem)

	# Clear all items and make sure only the image is left
	widget.clearAllItems()
	assert(0 == len(_view.scene().items()))

	# Re-add several items on the view
	i1=widget.addItem([[-10,-10],[20,20]], "item1")
	i2=widget.addItem([[100,100],[200,200]], "item2")
	i3=widget.addItem([[110,110],[200,200]], "item3")
	i4=widget.addItem([[120,120],[200,200]], "item4")

	# Make the scene fit the widget again
	qtbot.mouseClick(widget._widget.fit_button, QtCore.Qt.LeftButton)

	# If several objects are stacked, multiple clicks change the selection
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(130,180))
		                )
	assert("item4" == _s.args[0])
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(130,180))
		                )
	assert("item3" == _s.args[0])
	with qtbot.waitSignal(widget.itemSelected, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(130,180))
		                )
	assert("item2" == _s.args[0])

	# Set the widget as non-read-only
	widget.read_only = False

	# If we click on the image, a signal should be raised to add an item
	with qtbot.waitSignal(widget.itemAdditionRequested, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(250,250))
		                )

	# But the signal should not be raised if we click on an existing object
	with qtbot.assertNotEmitted(widget.itemAdditionRequested):
		qtbot.mouseClick(_view.viewport(),
	                 QtCore.Qt.LeftButton,
	                 0,
	                 _view.mapFromScene(QtCore.QPointF(130,180))
	                )

	# BTW, now item4 is selected

	# It is possible to move a selected object by dragging it with the mouse
	from_pos = _view.viewport().mapToGlobal(
	               _view.mapFromScene(QtCore.QPoint(180,180))
	           )
	to_pos = _view.viewport().mapToGlobal(
	             _view.mapFromScene(QtCore.QPoint(260,260))
	         )
	mouseDrag(qtbot,(from_pos.x(),from_pos.y()),(to_pos.x(), to_pos.y()))

	# Here the item has probably been moved, but their is a small uncertainty
	# on its position due to the resizing of the scene
	some_rect = _view.mapToScene(QtCore.QRect(0,0,100,100)).boundingRect()
	h_epsilon = int(some_rect.width() / 100.0)
	v_epsilon = int(some_rect.height() / 100.0)
	assert(i4.coordinates[0][0] in range(200-h_epsilon,201+h_epsilon))
	assert(i4.coordinates[0][1] in range(200-v_epsilon,201+v_epsilon))
	assert(i4.coordinates[1][0] in range(280-h_epsilon,281+h_epsilon))
	assert(i4.coordinates[1][1] in range(280-v_epsilon,281+v_epsilon))

	# Put the item back at the wanted position
	# (this is not the proper way to do it but...)
	r = i4.rect()
	top_left_pt = i4.mapFromScene(QtCore.QPoint(200, 200))
	bottom_right_pt = i4.mapFromScene(QtCore.QPoint(280, 280))
	r.setTop(top_left_pt.x())
	r.setLeft(top_left_pt.y())
	r.setRight(bottom_right_pt.x())
	r.setBottom(bottom_right_pt.y())
	i4.setRect(r)
	i4.coordinates = [[200,200],[280,280]]

	# A selected item can be resized, using the wheel, or the arrow keys
	mouseScroll(qtbot, 10)
	assert([[170,170],[310,310]] == i4.coordinates)

	qtbot.keyClick(_view.viewport(), QtCore.Qt.Key_Up)
	assert([[170,165],[310,315]] == i4.coordinates)
	qtbot.keyClick(_view.viewport(), QtCore.Qt.Key_Down)
	assert([[170,170],[310,310]] == i4.coordinates)
	qtbot.keyClick(_view.viewport(), QtCore.Qt.Key_Right)
	assert([[165,170],[315,310]] == i4.coordinates)
	qtbot.keyClick(_view.viewport(), QtCore.Qt.Key_Left)
	assert([[170,170],[310,310]] == i4.coordinates)

	# And finally, if a selected object is right-clicked, a "deletion" signal
	# is sent
	with qtbot.waitSignal(widget.itemDeletionRequested, timeout=500) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(250,250))
		                )
	assert(i4 == _s.args[0])

	# Same if DEL button is pushed
	with qtbot.waitSignal(widget.itemDeletionRequested, timeout=500) as _s:
		qtbot.keyClick(_view.viewport(), QtCore.Qt.Key_Delete)
	assert(i4 == _s.args[0])

	# And nothing happens if the clicked object is not selected
	widget.deselectAll()
	with qtbot.assertNotEmitted(widget.itemDeletionRequested) as _s:
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(250,250))
		                )

	# And if the click is not on an item
	with qtbot.assertNotEmitted(widget.itemDeletionRequested):
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(1000,1000))
		                )

	# The type of the object can be changed
	with qtbot.waitSignal(widget.objectTypeChanged, timeout=500) as _s:
		widget.type_selector.setCurrentIndex(
		    widget.type_selector.findText("AUDIO")
		)
	assert("AUDIO" == _s.args[0])

	# It can also be changed by a call
	with pytest.raises(KeyError):
		widget.setType("IMAGE_TOTO")
	widget.setType("IMAGE")


	# Back to read-only
	widget.read_only = True

	# No "addition" signal is sent when clicking on empty parts of the image
	with qtbot.assertNotEmitted(widget.itemAdditionRequested):
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(1000,1000))
		                )

	# And do "deletion" signal is sent when right-clicking on the selected item
	widget.selectItem(i4)
	assert(_view.scene()._selectedItem == i4)
	with qtbot.assertNotEmitted(widget.itemDeletionRequested):
		qtbot.mouseClick(_view.viewport(),
		                 QtCore.Qt.RightButton,
		                 0,
		                 _view.mapFromScene(QtCore.QPointF(250,250))
		                )

	# Selected object does not change size after key typing of wheel rolling
	mouseScroll(qtbot, 10)
	assert([[170,170],[310,310]] == i4.coordinates)
	qtbot.keyClick(_view.viewport(), QtCore.Qt.Key_Left)
	assert([[170,170],[310,310]] == i4.coordinates)

	# And selected object cannot be moved
	to_pos = _view.viewport().mapToGlobal(
	               _view.mapFromScene(QtCore.QPointF(180,180))
	           )
	from_pos = _view.viewport().mapToGlobal(
	             _view.mapFromScene(QtCore.QPointF(260,260))
	         )
	mouseDrag(qtbot,(from_pos.x(),from_pos.y()),(to_pos.x(), to_pos.y()))
	assert([[170,170],[310,310]] == i4.coordinates)
