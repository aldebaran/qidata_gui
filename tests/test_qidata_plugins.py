# -*- coding: utf-8 -*-
# Standard library
import subprocess
import time

def test_qidata_commands(jpg_file_path):
	# Make sure the commands are really defined upon installation
	subprocess.check_call(["qidata",
	                       "open",
	                       "-h"])

	subprocess.check_call(["qidata",
	                       "annotate",
	                       "-h"])

	subprocess.check_call(["qidata",
	                       "extract",
	                       "-h"])

def test_open_app(jpg_file_path):
	subprocess.check_call(["python",
	                       "-m",
	                       "qidata_apps.viewer.app",
	                       jpg_file_path])

def test_annotate_app(big_dataset_path):
	subprocess.check_call(["python",
	                       "-m",
	                       "qidata_apps.annotator.app",
	                       "sambrose",
	                       big_dataset_path])

def test_rosbag_extract_app(rosbag_asus_path):
	subprocess.check_call(["python",
	                       "-m",
	                       "qidata_apps.rosbag_extractor.app",
	                       rosbag_asus_path])

