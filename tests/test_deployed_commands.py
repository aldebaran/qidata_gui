# -*- coding: utf-8 -*-

# Standard library
import subprocess

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