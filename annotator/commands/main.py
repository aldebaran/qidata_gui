# -*- coding: utf-8 -*-

# Argparse
import argparse
try:
    import argcomplete
    has_argcomplete = True
except ImportError:
    has_argcomplete = False

# qidata
import annotator.version
from .annotate import AnnotateCommand

DESCRIPTION = "Annotate data-sets"

def make_command_parser(parent_parser=argparse.ArgumentParser(description=DESCRIPTION)):

    dataset_argument = parent_parser.add_argument("path", nargs="?", help="what to annotate")
    parent_parser.add_argument("-v", "--version", action=annotator.version.VersionAction, nargs=0,
                        help="print qidata release version number")
    if has_argcomplete:
        dataset_argument.completer = argcomplete.completers.DirectoriesCompleter()
    parent_parser.set_defaults(func=AnnotateCommand.run)
    return parent_parser

main_parser = make_command_parser()

