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