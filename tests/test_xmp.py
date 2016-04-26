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
				ald_prefix = f.libxmp_metadata.get_prefix_for_namespace(xmp.ALDEBARAN_NS)
				f.libxmp_metadata.set_property(schema_ns=xmp.ALDEBARAN_NS,
				                               prop_name=ald_prefix+"Property",
				                               prop_value="Value")
	def test_modify_readwrite(self):
		original_sha1 = sha1(self.jpg_path)
		with xmp.XMPFile(self.jpg_path, rw=True) as f:
			ald_prefix = f.libxmp_metadata.get_prefix_for_namespace(xmp.ALDEBARAN_NS)
			f.libxmp_metadata.set_property(schema_ns=xmp.ALDEBARAN_NS,
			                               prop_name=ald_prefix+"Property",
			                               prop_value="Value")
		modified_sha1 = sha1(self.jpg_path)
		self.assertNotEqual(original_sha1, modified_sha1)

class XMPTestCase(unittest.TestCase):
	def setUp(self):
		self.EXPECTED_NS_UIDS = fixtures.JPG_PHOTO_NS_UIDS

		self.xmp_file = xmp.XMPFile(fixtures.sandboxed(fixtures.JPG_PHOTO))
		self.xmp_file.__enter__()
		self.example_xmp = self.xmp_file.metadata

	def tearDown(self):
		self.xmp_file.__exit__(None, None, None)

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
	def setUp(self):
		super(XMPNamespace, self).setUp()
		self.exif_ns = self.example_xmp[libxmp.consts.XMP_NS_EXIF]

	def test_address(self):
		namespaces = self.example_xmp.namespaces
		read_uids  = [n.uid for n in namespaces]
		self.assertListEqual(read_uids, self.EXPECTED_NS_UIDS)

	def test_len(self):
		for ns_uid in self.EXPECTED_NS_UIDS:
			ns = self.example_xmp[ns_uid]
			self.assertEqual(len(ns), fixtures.JPG_PHOTO_NS_LEN[ns_uid])

	def test_getitem(self):
		self.assertIsInstance(self.exif_ns["LightSource"], xmp.XMPElement)
		self.assertIsInstance(self.exif_ns["Flash/Function"], xmp.XMPElement)
		self.assertIsInstance(self.exif_ns["exif:Flash/exif:Function"], xmp.XMPElement)
		with self.assertRaises(KeyError):
			self.exif_ns["Flashing"]
		with self.assertRaises(KeyError):
			self.exif_ns["Flash/Functioning"]

class TreeMixins(XMPTestCase):
	def setUp(self):
		super(TreeMixins, self).setUp()
		self.exif_ns = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.root_structure = self.exif_ns.Flash
		self.root_array = self.exif_ns.ISOSpeedRatings
		self.nested_structure = self.exif_ns.Flash.Function

	def test_namespace_uid(self):
		self.assertEqual(self.root_structure.namespace_uid, libxmp.consts.XMP_NS_EXIF)

	def test_is_top_level(self):
		self.assertTrue(self.root_structure.is_top_level)
		self.assertTrue(self.root_array.is_top_level)
		self.assertFalse(self.nested_structure.is_top_level)
		# TODO Array nested in array
		# TODO Struct nested in array

	def test_is_array_element(self):
		self.assertFalse(self.root_array.is_array_element)
		self.assertTrue(self.root_array[0].is_array_element)
		self.assertFalse(self.root_structure.is_array_element)
		self.assertFalse(self.nested_structure.is_array_element)

	def test_parent_address(self):
		self.assertIsNone(self.root_array.parent_address)
		self.assertIsNone(self.root_structure.parent_address)
		self.assertIsNotNone(self.nested_structure.parent_address)
		self.assertEqual(self.nested_structure.parent_address, "exif:Flash")
		self.assertEqual(self.root_array[0].parent_address, "exif:ISOSpeedRatings")

	def test_element_parent(self):
		self.assertIsNone(self.exif_ns.parent)
		self.assertIsInstance(self.root_structure.parent, xmp.XMPNamespace)
		self.assertIsInstance(self.root_array.parent, xmp.XMPNamespace)
		self.assertIsInstance(self.nested_structure.parent, xmp.XMPStructure)
		self.assertEqual(self.nested_structure.parent.name, "exif:Flash")
		self.assertIsInstance(self.nested_structure.parent.parent, xmp.XMPNamespace)

class XMPArray(XMPTestCase):
	def setUp(self):
		super(XMPArray, self).setUp()
		self.exif = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.iso_array = self.exif.ISOSpeedRatings
		self.components_array = self.exif.ComponentsConfiguration

	def test_len(self):
		self.assertEqual(len(self.iso_array), 1)
		self.assertEqual(len(self.components_array), 4)

	def test_getitem(self):
		self.assertEqual(self.iso_array[0].value, "400")

	def test_getitem_slices(self):
		self.assertEqual(self.iso_array[-1].value, "400")
		self.assertEqual(self.components_array[-1].value, "0")
		self.assertEqual([e.value for e in self.iso_array[:]], ["400"])
		self.assertEqual([e.value for e in self.components_array[:]], ["1", "2", "3", "0"])
		self.assertEqual([e.value for e in self.components_array[:-1]], ["1", "2", "3"])
		self.assertEqual([e.value for e in self.components_array[::2]], ["1", "3"])
		self.assertEqual([e.value for e in self.components_array[-3:-1]], ["2","3"])

class XMPStructure(XMPTestCase):
	def setUp(self):
		super(XMPStructure, self).setUp()
		self.exif_ns = self.example_xmp[libxmp.consts.XMP_NS_EXIF]
		self.tiff_metadata = self.example_xmp[libxmp.consts.XMP_NS_TIFF]

	def test_contains(self):
		self.assertTrue( "FNumber"  in self.exif_ns)
		self.assertFalse("FNumbers" in self.exif_ns)
		self.assertTrue( "ResolutionUnit"  in self.tiff_metadata)
		self.assertFalse("ResolutionUnits" in self.tiff_metadata)

	def test_has(self):
		self.assertTrue( self.exif_ns.has("FNumber"))
		self.assertFalse(self.exif_ns.has("FNumbers"))

		self.assertTrue( self.tiff_metadata.has("ResolutionUnit"))
		self.assertFalse(self.tiff_metadata.has("ResolutionUnits"))

	def test_getitem(self):
		self.assertEqual("32/10", self.exif_ns["FNumber"].value)
		with self.assertRaises(KeyError):
			self.exif_ns["inexistent_element"]

	def test_get(self):
		# Existing attribute
		self.assertIsInstance(self.exif_ns.get("FNumber"), xmp.XMPValue)
		self.assertEqual(self.exif_ns.get("FNumber").value, "32/10")
		# Non-existing attribute
		self.assertIsNone(self.exif_ns.get("inexistent_element"))

	def test_attribute_descriptor_get(self):
		self.assertEqual("32/10", self.exif_ns.FNumber.value)

	def test_getattr(self):
		# Existing attribute
		self.assertIsInstance(self.exif_ns.FNumber, xmp.XMPValue)
		self.assertEqual(self.exif_ns.FNumber.value, "32/10")
		# Non-existing attribute
		self.assertIsInstance(self.exif_ns.inexistent_element, xmp.XMPVirtualElement)
		# Nested attribute
		self.assertIsInstance(self.exif_ns.Flash, xmp.XMPStructure)
		self.assertIsInstance(self.exif_ns.Flash.RedEyeMode, xmp.XMPValue)
		self.assertEqual(self.exif_ns.Flash.RedEyeMode.value, "False")

	def test_setattr_existing(self):
		# Existing attribute
		jpg_filepath = fixtures.sandboxed(fixtures.JPG_PHOTO)
		with xmp.XMPFile(jpg_filepath, rw=True) as xmp_file:
			xmp_file.metadata[libxmp.consts.XMP_NS_EXIF].FNumber = "314/141"
		with xmp.XMPFile(jpg_filepath) as xmp_file:
			self.assertEqual(xmp_file.metadata[libxmp.consts.XMP_NS_EXIF].FNumber.value, "314/141")

	def test_setattr_inexistent(self):
		with xmp.XMPFile(fixtures.sandboxed(fixtures.JPG_PHOTO), rw=True) as xmp_file:
			xmp_file.metadata[xmp.ALDEBARAN_NS].inexistent_element = 12

class XMPVirtualElement(XMPTestCase):
	def setUp(self):
		super(XMPVirtualElement, self).setUp()
		self.exif_ns = self.example_xmp[libxmp.consts.XMP_NS_EXIF]

	def test_getattr(self):
		self.assertIsInstance(self.exif_ns.inexistent_element.nested_inexistent_element, xmp.XMPVirtualElement)
		self.assertIsInstance(self.exif_ns.inexistent_element[2], xmp.XMPVirtualElement)
		self.assertEqual(self.exif_ns.inexistent_element[2].address,
		                 "%s[2]" % self.exif_ns.inexistent_element.address)

	def test_parent(self):
		self.assertIsInstance(self.exif_ns.virtual_element.parent, xmp.XMPNamespace)
		self.assertIsInstance(self.exif_ns.virtual_element.nested_virtual_element.parent, xmp.XMPVirtualElement)
