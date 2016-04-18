#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import unittest
# Qidata
from qidata.dataitem import DataItem
from . import fixtures

class File(unittest.TestCase):
	def setUp(self):
		self.jpg_path = fixtures.sandboxed(fixtures.JPG_PHOTO)

	def test_contextmanager_noop(self):
		with DataItem(self.jpg_path):
			pass

	def test_metadata_access(self):
		with DataItem(self.jpg_path) as item:
			item.metadata

	def test_aldebaran_metadata_access(self):
		with DataItem(self.jpg_path) as item:
			item.metadata.aldebaran

class Metadata(unittest.TestCase):
	def setUp(self):
		self.jpg_data_item = DataItem(fixtures.sandboxed(fixtures.JPG_PHOTO))
		self.jpg_data_item.__enter__()

	def tearDown(self):
		self.jpg_data_item.__exit__(None, None, None)
