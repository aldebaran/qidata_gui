# -*- coding: utf-8 -*-

DESCRIPTION = "Get information about datasets and data-items"

class StatusCommand:
	@staticmethod
	def add_parser(parent_subparsers):
		parser = parent_subparsers.add_parser(__name__.split(".")[-1], description=DESCRIPTION)
		parser.set_defaults(func=StatusCommand.run)

	@staticmethod
	def run(args):
		pass
