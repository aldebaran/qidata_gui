# -*- coding: utf-8 -*-

# Standard Library
import errno
import os
import unittest
import shutil
# libXMP
import libxmp.consts
# Qidata
from qidata import xmp
from . import fixtures

def sha1(file_path):
	import hashlib
	hasher = hashlib.sha1()
	with open(file_path,'rb') as file:
		file_data = file.read()
	hasher.update(file_data)
	return hasher.hexdigest()

class XMPFile(unittest.TestCase):
	def setUp(self):
		self.jpg_path = fixtures.sandboxed(fixtures.JPG_PHOTO)

	def test_contextmanager_noop(self):
		original_sha1 = sha1(self.jpg_path)
		with xmp.XMPFile(self.jpg_path):
			pass
		noop_sha1 = sha1(self.jpg_path)
		self.assertEqual(original_sha1, noop_sha1)

	def test_modify_readonly(self):
		with self.assertRaises(RuntimeWarning):
			with xmp.XMPFile(self.jpg_path) as f:
				ald_prefix = f.libxmp_metadata.get_prefix_for_namespace(xmp.ALDEBARAN_NS_1)
				f.libxmp_metadata.set_property(schema_ns=xmp.ALDEBARAN_NS_1,
				                               prop_name=ald_prefix+"Property",
				                               prop_value="Value")
	def test_modify_readwrite(self):
		original_sha1 = sha1(self.jpg_path)
		with xmp.XMPFile(self.jpg_path, rw=True) as f:
			ald_prefix = f.libxmp_metadata.get_prefix_for_namespace(xmp.ALDEBARAN_NS_1)
			f.libxmp_metadata.set_property(schema_ns=xmp.ALDEBARAN_NS_1,
			                               prop_name=ald_prefix+"Property",
			                               prop_value="Value")
		modified_sha1 = sha1(self.jpg_path)
		self.assertNotEqual(original_sha1, modified_sha1)

class XMPTestCase(unittest.TestCase):
	def setUp(self):
		with xmp.XMPFile(fixtures.sandboxed(fixtures.JPG_PHOTO)) as xmp_file:
			self.example_xmp = xmp_file.metadata
			self.EXPECTED_NS_UIDS = fixtures.JPG_PHOTO_NS_UIDS

class XMP(XMPTestCase):
	def test_empty_init(self):
		empty_xmp = xmp.XMPMetadata()
		self.assertEqual(len(empty_xmp.namespaces), 0)

	def test_len(self):
		self.assertEqual(len(self.example_xmp), 4)

	def test_namespaces_property_types(self):
		namespaces = self.example_xmp.namespaces
		self.assertIsInstance(namespaces, list)
		self.assertTrue(all([isinstance(n,xmp.XMPNamespace) for n in namespaces]))

	def test_getitem(self):
		for ns_uid in self.EXPECTED_NS_UIDS:
			self.assertIsInstance(self.example_xmp[ns_uid], xmp.XMPNamespace)

	def test_create_namespace(self):
		empty_xmp = xmp.XMPMetadata()
		self.assertEqual(len(empty_xmp.namespaces), 0)

class XMPNamespace(XMPTestCase):
	def test_address(self):
		namespaces = self.example_xmp.namespaces
		read_uids  = [n.uid for n in namespaces]
		self.assertListEqual(read_uids, self.EXPECTED_NS_UIDS)

	def test_len(self):
		for ns_uid in self.EXPECTED_NS_UIDS:
			ns = self.example_xmp[ns_uid]
			self.assertEqual(len(ns), fixtures.JPG_PHOTO_NS_LEN[ns_uid])

class XMPStructure(XMPTestCase):
	def test_contains(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.assertTrue( "FNumber"  in exif_metadata)
		self.assertFalse("FNumbers" in exif_metadata)

		tiff_metadata = self.example_xmp[libxmp.consts.XMP_NS_TIFF]
		self.assertTrue( "ResolutionUnit"  in tiff_metadata)
		self.assertFalse("ResolutionUnits" in tiff_metadata)


	def test_has(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.assertTrue( exif_metadata.has("FNumber"))
		self.assertFalse(exif_metadata.has("FNumbers"))

		tiff_metadata = self.example_xmp[libxmp.consts.XMP_NS_TIFF]
		self.assertTrue( tiff_metadata.has("ResolutionUnit"))
		self.assertFalse(tiff_metadata.has("ResolutionUnits"))

	def test_getitem(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.assertEqual("32/10", exif_metadata["FNumber"].value)
		with self.assertRaises(KeyError):
			exif_metadata["inexistent_element"]

	def test_get(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		# Existing attribute
		self.assertIsInstance(exif_metadata.get("FNumber"), xmp.XMPValue)
		self.assertEqual(exif_metadata.get("FNumber").value, "32/10")
		# Non-existing attribute
		self.assertIsNone(exif_metadata.get("inexistent_element"))

	def test_attribute_descriptor_get(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.assertEqual("32/10", exif_metadata.FNumber.value)

	def test_getattr(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		# Existing attribute
		self.assertIsInstance(exif_metadata.FNumber, xmp.XMPValue)
		self.assertEqual(exif_metadata.FNumber.value, "32/10")
		# Non-existing attribute
		self.assertIsInstance(exif_metadata.inexistent_element, xmp.XMPVirtualElement)

	def test_setattr(self):
		exif_metadata = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		# Existing attribute
		exif_metadata.FNumber = "314/141"
		# Non-existing attribute
		exif_metadata.inexistent_element = 12
