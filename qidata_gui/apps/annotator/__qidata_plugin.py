# -*- coding: utf-8 -*-

# Third-party libraries
import argparse
try:
	import argcomplete
	has_argcomplete = True
except ImportError:
	has_argcomplete = False

# Local modules
from app import main

DESCRIPTION = "Annotate data-sets"

def make_command_parser(parent_parser=argparse.ArgumentParser(description=DESCRIPTION)):

	dataset_argument = parent_parser.add_argument("path", nargs="?", help="what to annotate", default=".")

	if has_argcomplete:
		dataset_argument.completer = argcomplete.completers.DirectoriesCompleter()
		parent_parser.set_defaults(func=lambda x:main([x.path]))
	return parent_parser