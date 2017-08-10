# -*- coding: utf-8 -*-

# Standard libraries
import argparse
import sys

# Third-party libraries
import qidata

# Local modules
from qidata_apps import QiDataApp
from qidata_gui import QiDataSensorWidget

class App(QiDataApp):

	# ───────────
	# Constructor

	def __init__(self, filename, writer):
		self.filename = filename
		if writer is None:
			self.qidata_object = qidata.open(self.filename)
			writer = ""
		else:
			self.qidata_object = qidata.open(self.filename, "w")

		QiDataApp.__init__(self, "QiData Viewer")
		# Add a reference to the qidata object in main window so that it can
		# be saved properly or not upon closure
		self.main_window.qidata_object = self.qidata_object

		try:
			self.main_window.main_widget = QiDataSensorWidget(
			                                   self.qidata_object,
			                                   writer
			                               )
		except Exception:
			self.qidata_object.close()
			raise

		self.main_window.setWindowTitle("QiData Viewer: "+filename)

	# ──────────
	# Public API

	def run(self):
		try:
			super(App, self).run()
		finally:
			self.qidata_object.close()

def main(args):
	qidata_app = App(args.path, args.writer)
	try:
		qidata_app.run()
	except KeyboardInterrupt:
		pass

# ─────────────────────────────
# Definitions for Qidata plugin

DESCRIPTION = "Opens a viewer to display a QiDataSensorFile"

def make_command_parser(parser=argparse.ArgumentParser(description=DESCRIPTION)):
	file_arg = parser.add_argument("path", help="Path of the file to open")
	writer_arg = parser.add_argument("-w",
	                                 "--writer",
	                                 nargs="?",
	                                 const="",
	                                 help="Open the file in 'w' mode. Specify \
	                                 a writer to be able to add new annotations"
	                                )
	parser.set_defaults(func=main)
	return parser

# ───────────────────
# Add a main launcher

if __name__ == "__main__":
	parser = make_command_parser()
	parsed_args = parser.parse_args(sys.argv[1:])
	parsed_args.func(parsed_args)