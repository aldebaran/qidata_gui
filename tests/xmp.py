# Standard Library
import unittest
# Qidata
from qidata import xmp



class Editor(unittest.TestCase):
	def test_upper(self):
		self.assertEqual('foo'.upper(), 'FOOs')
		print "sdf"
