# -*- coding: utf-8 -*-

# Standard Library
import os

# Local modules
from qidata import DataType, QiDataSet
from qidata.metadata_objects import Context
from qidata_apps.rosbag_extractor.lib import makeQiDataSetFromROSbag

def test_create_dataset_from_rosbag(rosbag_asus_path):
	output_ds = os.path.splitext(rosbag_asus_path)[0]
	c=Context()
	c.recorder_names.append("mohamed.djabri")

	makeQiDataSetFromROSbag(rosbag_asus_path,
	    {
	        "/asus/camera/front/image_raw":("front",DataType.IMAGE_2D),
	        "/asus/camera/depth/image_raw":("depth",DataType.IMAGE_3D),
	        "/asus/camera/ir/image_raw":("ir",DataType.IMAGE_IR),
	    },
	    c
	)
	with QiDataSet(output_ds, "r") as _ds:
		assert(
		    set([DataType.IMAGE_IR,
		         DataType.IMAGE_2D,
		         DataType.IMAGE_3D]
		       ) == _ds.datatypes_available)
		assert(144 == len(_ds.children))
		s = _ds.getAllStreams()
		assert(3 == len(s))
		assert(s.has_key("front"))
		assert(s.has_key("depth"))
		assert(s.has_key("ir"))
		depth_stream_ref = map(
			                    lambda x: x[0]%x[1],
			                    zip(["depth_%02d.png"]*52, range(0,52))
			                  )
		depth_stream = _ds.getStream("depth")
		depth_stream_ts = depth_stream.keys()
		depth_stream_ts.sort()
		depth_stream_files = [depth_stream[ts] for ts in depth_stream_ts]
		assert(depth_stream_ref == depth_stream_files)
		assert((1455891947,72141784) == depth_stream_ts[0])
		with _ds.openChild("depth_00.png") as _f:
			assert(1455891946 == _f.timestamp.seconds)
			assert(879184270 == _f.timestamp.nanoseconds)
			assert(0.0059574200344 == _f.transform.translation.x)
			assert(0.0353449552978 == _f.transform.translation.y)
			assert(1.11488970044 == _f.transform.translation.z)
			assert(-0.473571741487 == _f.transform.rotation.x)
			assert(0.477636683954 == _f.transform.rotation.y)
			assert(-0.520649197032 == _f.transform.rotation.z)
			assert(0.525849234512 == _f.transform.rotation.w)
			assert(DataType.IMAGE_3D == _f.type)
		assert(0 == len(_ds.getAllFrames()))
		assert(["mohamed.djabri"] == _ds.context.recorder_names)
