# -*- coding: utf-8 -*-

# Standard libraries
import argparse
import os.path
import sys

# Third-party libraries
from PySide import QtGui
from PySide.QtGui import QApplication, QInputDialog, QMessageBox
import qidata

# Local modules
from qidata_gui import QiDataSensorWidget

class App(QApplication):

	# ───────────
	# Constructor

	def __init__(self, filename):
		QApplication.__init__(self, [])
		self.filename = filename
		self.qidata_object = qidata.open(self.filename)
		try:
			self.main_widget = QiDataSensorWidget(self.qidata_object)
			self.main_widget.setWindowTitle(filename)
		except Exception:
			self.qidata_object.close()
			raise

	# ──────────
	# Public API

	def run(self):
		try:
			self.main_widget.show()
			self.exec_()
		except KeyboardInterrupt:
			pass
		finally:
			self.qidata_object.close()

def main(args):
	qidata_app = App(args.path)
	try:
		qidata_app.run()
	except KeyboardInterrupt:
		pass

# ─────────────────────────────
# Definitions for Qidata plugin

DESCRIPTION = "Opens a viewer to display a QiDataSensorFile"

def make_command_parser(parser=argparse.ArgumentParser(description=DESCRIPTION)):
	file_arg = parser.add_argument("path", help="Path of the file to open")
	parser.set_defaults(func=main)
	return parser

# ───────────────────
# Add a main launcher

if __name__ == "__main__":
	parser = make_command_parser()
	parsed_args = parser.parse_args(sys.argv[1:])
	parsed_args.func(parsed_args)