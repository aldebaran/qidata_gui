
# Third-party libraries
from PySide import QtCore, QtGui

# Local modules
from qidata_gui._subwidgets import (
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
