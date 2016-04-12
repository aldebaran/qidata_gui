#!/usr/bin/env python2
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

DATA_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
TEMPORARY_FOLDER = "/tmp/qidata/"

# ───────────
# Groundtruth

JPG_PHOTO_FILE = "SpringNebula.jpg"
JPG_PHOTO_FILE_NS_UIDS = [
	libxmp.consts.XMP_NS_EXIF,
	libxmp.consts.XMP_NS_TIFF,
	libxmp.consts.XMP_NS_XMP,
	libxmp.consts.XMP_NS_Photoshop
]
JPG_PHOTO_FILE_NS_LEN = {
	libxmp.consts.XMP_NS_EXIF      : 31,
	libxmp.consts.XMP_NS_TIFF      : 7,
	libxmp.consts.XMP_NS_XMP       : 3,
	libxmp.consts.XMP_NS_Photoshop : 1,
}

def sha1(file_path):
	import hashlib
	hasher = hashlib.sha1()
	with open(file_path,'rb') as file:
		file_data = file.read()
	hasher.update(file_data)
	return hasher.hexdigest()

class XMPFile(unittest.TestCase):
	def setUp(self):
		self.original_jpg_photo_path = os.path.join(DATA_FOLDER, JPG_PHOTO_FILE)
		self.jpg_photo_path = os.path.join(TEMPORARY_FOLDER, JPG_PHOTO_FILE)

		# Make a copy of test files in /tmp
		try:
			os.mkdir(TEMPORARY_FOLDER)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		shutil.copyfile(self.original_jpg_photo_path, self.jpg_photo_path)

	def test_noop(self):
		original_sha1 = sha1(self.jpg_photo_path)
		with xmp.XMPFile(self.jpg_photo_path):
			pass
		noop_sha1 = sha1(self.jpg_photo_path)
		self.assertEqual(original_sha1, noop_sha1)

	def test_modify_readonly(self):
		with self.assertRaises(RuntimeWarning):
			with xmp.XMPFile(self.jpg_photo_path) as f:
				ald_prefix = f.libxmp_metadata.get_prefix_for_namespace(xmp.XMP_NS_ALDEBARAN)
				f.libxmp_metadata.set_property(schema_ns=xmp.XMP_NS_ALDEBARAN,
				                               prop_name=ald_prefix+"Property",
				                               prop_value="Value")
	def test_modify_readwrite(self):
		original_sha1 = sha1(self.jpg_photo_path)
		with xmp.XMPFile(self.jpg_photo_path, rw=True) as f:
			ald_prefix = f.libxmp_metadata.get_prefix_for_namespace(xmp.XMP_NS_ALDEBARAN)
			f.libxmp_metadata.set_property(schema_ns=xmp.XMP_NS_ALDEBARAN,
			                               prop_name=ald_prefix+"Property",
			                               prop_value="Value")
		modified_sha1 = sha1(self.jpg_photo_path)
		self.assertNotEqual(original_sha1, modified_sha1)

class XMPTestCase(unittest.TestCase):
	def setUp(self):
		with xmp.XMPFile(os.path.join(DATA_FOLDER, JPG_PHOTO_FILE)) as xmp_file:
			self.example_xmp = xmp_file.metadata
			self.EXPECTED_NS_UIDS = JPG_PHOTO_FILE_NS_UIDS

class XMP(XMPTestCase):
	def test_empty_init(self):
		empty_xmp = xmp.XMP()
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
		empty_xmp = xmp.XMP()
		self.assertEqual(len(empty_xmp.namespaces), 0)

class XMPNamespace(XMPTestCase):
	def test_address(self):
		namespaces = self.example_xmp.namespaces
		read_uids  = [n.uid for n in namespaces]
		self.assertListEqual(read_uids, self.EXPECTED_NS_UIDS)

	def test_len(self):
		for ns_uid in self.EXPECTED_NS_UIDS:
			ns = self.example_xmp[ns_uid]
			self.assertEqual(len(ns), JPG_PHOTO_FILE_NS_LEN[ns_uid])
