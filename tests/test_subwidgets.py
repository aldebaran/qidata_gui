
# Third-party libraries
from PySide import QtCore, QtGui

# Local modules
from qidata_gui._subwidgets import (
                                    SelectableListWidget,
                                    TickableListWidget,
                                   )

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

	# Once an object is removed, clicking on it does not
	# trigger any signal
	widget.removeItem(i2)
	with qtbot.assertNotEmitted(widget.itemSelected):
		qtbot.mouseClick(widget.viewport(),
		                 QtCore.Qt.LeftButton,
		                 0,
		                 rect2.center())

