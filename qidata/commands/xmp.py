#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Argparse
import argparse
try:
	import argcomplete
	has_argcomplete = True
except ImportError:
	has_argcomplete = False
# Qidata
from qidata.xmp import XMPFile

DESCRIPTION = "Manipulate XMP metadata"

class XMPCommand:
	@staticmethod
	def add_parser(parent_subparsers):
		parser = parent_subparsers.add_parser(__name__.split(".")[-1],
		                                      description=DESCRIPTION)
		subparsers = parser.add_subparsers()

		# ────────────────
		# show sub-command

		show_parser = subparsers.add_parser("show", description="show XMP")
		file_argument = show_parser.add_argument("file", help="what to examine")
		if has_argcomplete: file_argument.completer = argcomplete.completers.FilesCompleter()
		show_parser.set_defaults(func=XMPCommand.show)

		# ───────────────
		# xml sub-command

		xml_parser = subparsers.add_parser("xml", description="show XMP as XML")
		file_argument = xml_parser.add_argument("file", help="what to examine")
		if has_argcomplete: file_argument.completer = argcomplete.completers.FilesCompleter()
		xml_parser.set_defaults(func=XMPCommand.xml)

	@staticmethod
	def show(args):
		input_file_path = args.file
		with XMPFile(input_file_path) as xmp_file:
			print xmp_file

	@staticmethod
	def xml(args):
		import sys
		input_file_path = args.file
		with XMPFile(input_file_path) as xmp_file:
			print xmp_file.metadata.xml()
