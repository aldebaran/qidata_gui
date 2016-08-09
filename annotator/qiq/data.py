# -*- coding: utf-8 -*-

try:
	import qiq
	has_qiq = True
except ImportError:
	has_qiq = False

if has_qiq:
	import qiq.command
	import qidata.commands.main

	class DataCommand(qiq.command.Command):
		@staticmethod
		def add_parser(parent_subparsers, robot_override):
			qiq_data_parser = parent_subparsers.add_parser(__name__.split(".")[-1],
			                                               description=qidata.commands.main.DESCRIPTION)

			for sc in qidata.commands.main.SUBCOMMANDS:
				sc.add_parser(qiq_data_parser)
