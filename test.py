#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import unittest

TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"tests"))
sys.path.append(TEST_DIR)
os.chdir(TEST_DIR)

tests = unittest.TestLoader().discover(start_dir=TEST_DIR)
unittest.TextTestRunner(verbosity=2).run(tests)
