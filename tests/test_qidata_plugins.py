# -*- coding: utf-8 -*-
# Standard library
import subprocess
import time

def test_qidata_open_command(jpg_file_path):
	p=subprocess.Popen(["qidata",
	                    "open",
	                    jpg_file_path])
	time.sleep(1)
	p.terminate()

def test_qidata_open_app(jpg_file_path):
	subprocess.check_call(["qidata",
	                       "open",
	                       jpg_file_path])
