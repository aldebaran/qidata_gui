# -*- coding: utf-8 -*-

# Standard libraries
import os

# Third-party libraries
from PySide import QtGui

# Local modules
from qidata_apps import viewer, annotator

def test_open_app(jpg_file_path):
	# Create app, then close it (and close its file)
	a=viewer.app.App(jpg_file_path, None)
	a.main_window.main_widget.close()
	a.qidata_object.close()

def test_annotator_app(big_dataset_path, mock):
	# Create app, select a file, then close everything
	a=annotator.app.App(big_dataset_path, "jdoe")
	a.setSelected(os.path.join(big_dataset_path,"depth_00.png"))
	_g = mock.patch.object(QtGui.QMessageBox,'question',
	                       return_value=QtGui.QMessageBox.No)
	a.setSelected(os.path.join(big_dataset_path,"depth_01.png"))
	a.opened_qidata_object.close()
