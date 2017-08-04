# -*- coding: utf-8 -*-
# Standard library
import subprocess

def test_open_command():
	subprocess.check_call(["qidata",
	                       "open",
	                       "tests/data/SpringNebula.jpg"])