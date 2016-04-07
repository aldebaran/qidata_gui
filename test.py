#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os.path
import unittest

TEST_DIR = os.path.join(os.path.dirname(__file__),"tests")

tests = unittest.TestLoader().discover(start_dir=TEST_DIR, pattern="*.py")
unittest.TextTestRunner(verbosity=2).run(tests)
