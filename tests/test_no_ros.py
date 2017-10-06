# -*- coding: utf-8 -*-

# Standard Library
import pytest

# Local modules
from qidata import DataType
from qidata.metadata_objects import Context
from qidata_apps.rosbag_extractor.lib import makeQiDataSetFromROSbag
from qidata_apps.rosbag_extractor.app import main

def test_cannot_create_dataset(rosbag_asus_files):
	rosbag_asus_path = rosbag_asus_files[0]
	with pytest.raises(Exception) as _e:
		makeQiDataSetFromROSbag(rosbag_asus_path,
		    {
		        "/asus/camera/front/image_raw":("front",DataType.IMAGE_2D, rosbag_asus_files[1], ""),
		        "/asus/camera/depth/image_raw":("depth",DataType.IMAGE_3D, rosbag_asus_files[2], ""),
		        "/asus/camera/ir/image_raw":("ir",DataType.IMAGE_IR, rosbag_asus_files[2], ""),
		    },
		    Context()
		)
	assert("ROS python package were not found. Did you source the environment ?" == _e.value.message)

def test_failing_import():
	with pytest.raises(ImportError):
		from qidata_apps.rosbag_extractor.app import App
	with pytest.raises(ImportError):
		from qidata_apps.rosbag_extractor.app import MainWidget

def test_failing_main():
	with pytest.raises(RuntimeError):
		main(None)