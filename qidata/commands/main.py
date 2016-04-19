# -*- coding: utf-8 -*-

# Argparse
import argparse
# qidata
from . import annotate, status, xmp
import qidata.version

DESCRIPTION = "Manage data-sets"
SUBCOMMANDS = [status.StatusCommand,
               annotate.AnnotateCommand,
               xmp.XMPCommand]

def parser():
	parser = argparse.ArgumentParser(description=DESCRIPTION)
	subparsers = parser.add_subparsers()
	for sc in SUBCOMMANDS:
		sc.add_parser(subparsers)
	parser.add_argument("-v", "--version", action=qidata.version.VersionAction, nargs=0,
	                    help="print qidata release version number")
	return parser

main_parser = parser()
