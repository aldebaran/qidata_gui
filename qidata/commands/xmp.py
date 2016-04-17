#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import os.path
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

		# ───────────────
		# set sub-command

		set_parser = subparsers.add_parser("set", description="modify an XMP property")
		file_argument      = set_parser.add_argument("file", help="file to modify")
		namespace_argument = set_parser.add_argument("namespace", help="namespace to operate on")
		property_argument  = set_parser.add_argument("property", help="XMP property to set")
		value_argument     = set_parser.add_argument("value", help="XMP property to set")
		if has_argcomplete: file_argument.completer = argcomplete.completers.FilesCompleter()
		set_parser.set_defaults(func=XMPCommand.set)

		# ──────────────────
		# delete sub-command

		delete_parser = subparsers.add_parser("delete", description="delete an XMP property")
		file_argument      = delete_parser.add_argument("file", help="file to modify")
		namespace_argument = delete_parser.add_argument("namespace", help="namespace to operate on")
		property_argument  = delete_parser.add_argument("property", help="XMP property to set")
		if has_argcomplete: file_argument.completer = argcomplete.completers.FilesCompleter()
		delete_parser.set_defaults(func=XMPCommand.delete)

	@staticmethod
	def show(args):
		throwIfAbsent(args.file)
		input_file_path = args.file
		with XMPFile(input_file_path) as xmp_file:
			print xmp_file

	@staticmethod
	def xml(args):
		throwIfAbsent(args.file)
		input_file_path = args.file
		with XMPFile(input_file_path) as xmp_file:
			print xmp_file.metadata.xml()

	@staticmethod
	def set(args):
		throwIfAbsent(args.file)
		print "Setting property {ns}:{p} of file {f} to {v}".format(ns=args.namespace,
		                                                             p=args.property,
		                                                             v=args.value,
		                                                             f=args.file)
		input_file_path = args.file
		with XMPFile(input_file_path) as xmp_file:
			pass
			# TODO

	@staticmethod
	def delete(args):
		throwIfAbsent(args.file)
		print "Deleting property {ns}:{p} of file {f}".format(ns=args.namespace,
		                                                       p=args.property,
		                                                       v=args.value,
		                                                       f=args.file)
		input_file_path = args.file
		with XMPFile(input_file_path) as xmp_file:
			pass
			# TODO

# ───────
# Helpers

def throwIfAbsent(file_path):
	if not os.path.isfile(file_path):
		import sys
		sys.exit("File "+file_path+" doesn't exist")
