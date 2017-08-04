
# Third-party libraries
import cv2
from PySide import QtCore, QtGui
import qidata
from qidata.metadata_objects import Property

# Local modules
from qidata_gui._subwidgets import (
                                    SelectableListWidget,
                                    TickableListWidget,
                                   )
from qidata_gui import QiDataSensorWidget

def test_qidatasensor_widget(qtbot, jpg_file_path):

	# Create widget
	_f = qidata.open(jpg_file_path)
	widget = QiDataSensorWidget(_f)
	widget.show()
	qtbot.addWidget(widget)

	# Click on localized annotation
	qtbot.mouseClick(widget.raw_data_viewer._widget.view.viewport(),
		             QtCore.Qt.LeftButton,
		             0,
		             widget.raw_data_viewer._widget.view.mapFromScene(
		                 QtCore.QPointF(110,180)
		             ))
	qtbot.wait(100)
	assert(
	    Property(key="key", value="value") == widget.annotation_displayer.data
	)
	assert("Property" == widget.type_selector.currentText())

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

	widget.annotators_list.item(1).setCheckState(QtCore.Qt.Unchecked)
	assert(1 == len(widget.raw_data_viewer._widget.view.scene().items()))

	widget.annotators_list.item(0).setCheckState(QtCore.Qt.Unchecked)
	assert(0 == widget.global_annotation_displayer.count())

	_f.close()
