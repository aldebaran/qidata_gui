# -*- coding: utf-8 -*-

# Standard Library
import unittest
# Qidata
from qidata.dataitem import DataItem
import qidata.xmp
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
		self.jpg_data_item.open()
		self.jpg_metadata = self.jpg_data_item.metadata

	def tearDown(self):
		self.jpg_data_item.close()

	def test_virtual_element(self):
		self.jpg_metadata.inexistent_attribute

	def test_nested_virtual_element(self):
		self.jpg_metadata.inexistent_attribute.nested_inexistent_attribute

	def test_virtual_element_descriptor_get(self):
		self.assertIsInstance(self.jpg_metadata.inexistent_attribute, qidata.xmp.XMPVirtualElement)
		self.assertIsInstance(self.jpg_metadata.__dict__, dict)

	def test_virtual_element_descriptor_set_readonly(self):
		self.jpg_metadata.inexistent_attribute = 12
		import warnings
		with warnings.catch_warnings(record=True) as w:
			warnings.simplefilter("always")
			self.jpg_data_item.close()
			self.assertEqual(len(w), 1)
			self.assertEqual(w[-1].category, RuntimeWarning)

		self.jpg_data_item.open()

	def test_virtual_element_descriptor_set(self):
		with DataItem(fixtures.sandboxed(fixtures.JPG_PHOTO), rw = True) as dataitem:
			dataitem.metadata.inexistent_attribute = 12
			self.assertIsInstance(dataitem.metadata.inexistent_attribute, qidata.xmp.XMPValue)
			self.assertEqual(dataitem.metadata.inexistent_attribute.value, "12")

	def test_virtual_element_descriptor_delete(self):
		with self.assertRaises(TypeError):
			del self.jpg_metadata.inexistent_attribute
