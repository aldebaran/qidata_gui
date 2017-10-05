# -*- coding: utf-8 -*-

# Copyright (c) 2017, Softbank Robotics Europe
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Standard Library
import os

# Local modules
from qidata import DataType, QiDataSet
from qidata.metadata_objects import Context
from qidata_apps.rosbag_extractor.lib import makeQiDataSetFromROSbag

def test_create_dataset_from_asus_rosbag(rosbag_asus_files):
	rosbag_asus_path = rosbag_asus_files[0]
	output_ds = os.path.splitext(rosbag_asus_path)[0]
	c=Context()
	c.recorder_names.append("mohamed.djabri")

	makeQiDataSetFromROSbag(rosbag_asus_path,
	    {
	        "/asus/camera/front/image_raw":("front",DataType.IMAGE_2D, rosbag_asus_files[1], ""),
	        "/asus/camera/depth/image_raw":("depth",DataType.IMAGE_3D, rosbag_asus_files[2], ""),
	        "/asus/camera/ir/image_raw":("ir",DataType.IMAGE_IR, rosbag_asus_files[2], ""),
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
			assert(262.5 == _f.raw_data.camera_info.camera_matrix[0][0])
			assert(262.5 == _f.raw_data.camera_info.projection_matrix[0][0])
			assert([] == _f.raw_data.camera_info.distortion_coeffs)
		assert(0 == len(_ds.getAllFrames()))
		assert(["mohamed.djabri"] == _ds.context.recorder_names)
