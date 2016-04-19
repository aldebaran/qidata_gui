# -*- coding: utf-8 -*-

# Argparse
import argparse
try:
	import argcomplete
	has_argcomplete = True
except ImportError:
	has_argcomplete = False
# qidata
from qidata.gui.app import QiDataApp

DESCRIPTION = "Annotate data-sets"

class AnnotateCommand:
	@staticmethod
	def add_parser(parent_subparsers):
		parser = parent_subparsers.add_parser(__name__.split(".")[-1],
		                                      description=DESCRIPTION)
		dataset_argument = parser.add_argument("path", nargs="?", help="what to annotate")
		if has_argcomplete:
			dataset_argument.completer = argcomplete.completers.DirectoriesCompleter()
		parser.set_defaults(func=AnnotateCommand.run)

	@staticmethod
	def run(args):
		qidata_app = QiDataApp(args.path)
		try:
			qidata_app.run()
		except KeyboardInterrupt:
			pass
