#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import errno
import os
import shutil
# libXMP
import libxmp.consts

# ──────────
# Parameters

DATA_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
SANDBOX_FOLDER = "/tmp/qidata/"

# ───────────
# Groundtruth

JPG_PHOTO = "SpringNebula.jpg"
JPG_PHOTO_NS_UIDS = [
	libxmp.consts.XMP_NS_EXIF,
	libxmp.consts.XMP_NS_TIFF,
	libxmp.consts.XMP_NS_XMP,
	libxmp.consts.XMP_NS_Photoshop
]
JPG_PHOTO_NS_LEN = {
	libxmp.consts.XMP_NS_EXIF      : 31,
	libxmp.consts.XMP_NS_TIFF      : 7,
	libxmp.consts.XMP_NS_XMP       : 3,
	libxmp.consts.XMP_NS_Photoshop : 1,
}

# ─────────
# Utilities

def sandboxed(file_path):
	"""
	Makes a copy of the given file in /tmp and returns its path.
	"""
	source_path = os.path.join(DATA_FOLDER,    file_path)
	tmp_path    = os.path.join(SANDBOX_FOLDER, file_path)

	try:
		os.mkdir(SANDBOX_FOLDER)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	shutil.copyfile(source_path, tmp_path)

	return tmp_path
