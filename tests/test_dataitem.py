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

	def test_metadata_attribute(self):
		with DataItem(self.jpg_path) as dataitem:
			dataitem.metadata

	def test_xmp_attribute(self):
		with DataItem(self.jpg_path) as dataitem:
			dataitem.xmp

class Metadata(unittest.TestCase):
	def setUp(self):
		self.jpg_data_item = DataItem(fixtures.sandboxed(fixtures.JPG_PHOTO))
		self.jpg_data_item.__enter__()
		self.jpg_metadata = self.jpg_data_item.metadata

	def tearDown(self):
		self.jpg_data_item.__exit__(None, None, None)

	def test_virtual_element(self):
		self.jpg_metadata.inexistent_attribute

	def test_nested_virtual_element(self):
		self.jpg_metadata.inexistent_attribute.nested_inexistent_attribute

	def test_virtual_element_descriptor_get(self):
		self.jpg_metadata.inexistent_attribute

	def test_virtual_element_descriptor_set(self):
		self.jpg_metadata.inexistent_attribute = 12

	def test_virtual_element_descriptor_delete(self):
		with self.assertRaises(AttributeError):
			del self.jpg_metadata.inexistent_attribute
