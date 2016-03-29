#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Argparse
import argparse
# qidata
import qidata.gui.annotator

DESCRIPTION = "Annotate data-sets"

class AnnotateCommand:
	@staticmethod
	def add_parser(parent_subparsers):
		parser = parent_subparsers.add_parser(__name__.split(".")[-1],
		                                      description=DESCRIPTION)
		parser.add_argument("dataset", nargs="?", help="what to annotate")
		parser.set_defaults(func=AnnotateCommand.run)

	@staticmethod
	def run(args):
		annotator = qidata.gui.annotator.Annotator()
		try:
			annotator.run()
		except KeyboardInterrupt:
			pass
