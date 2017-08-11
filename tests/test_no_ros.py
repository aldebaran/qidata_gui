# -*- coding: utf-8 -*-

# Standard Library
import pytest

# Local modules
from qidata import DataType
from qidata.metadata_objects import Context
from qidata_apps.rosbag_extractor.lib import makeQiDataSetFromROSbag

def test_cannot_create_dataset(rosbag_asus_path):
	with pytest.raises(Exception):
		makeQiDataSetFromROSbag(rosbag_asus_path,
		    {
		        "/asus/camera/front/image_raw":("front",DataType.IMAGE_2D),
		        "/asus/camera/depth/image_raw":("depth",DataType.IMAGE_3D),
		        "/asus/camera/ir/image_raw":("ir",DataType.IMAGE_IR),
		    },
		    Context()
		)
