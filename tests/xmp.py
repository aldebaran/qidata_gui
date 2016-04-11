# Standard Library
import errno
import os
import unittest
import shutil
# Qidata
from qidata import xmp

DATA_FOLDER = "./data/"
JPG_PHOTO_FILE = "SpringNebula.jpg"
TEMPORARY_FOLDER = "/tmp/qidata/"

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

class XMP(unittest.TestCase):
	def setUp(self):
		with xmp.XMPFile(os.path.join(DATA_FOLDER, JPG_PHOTO_FILE)) as xmp_file:
			self.example_xmp = xmp_file.metadata

	def test_len(self):
		self.assertEqual(len(self.example_xmp), 4)
