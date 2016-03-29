#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import sys
# PySide
from PySide.QtGui import QApplication
# qidata
from . import annotator_window

class Annotator(QApplication):
    def __init__(self):
        super(Annotator, self).__init__([])
        self.main_window = annotator_window.AnnotatorWindow()

    def run(self):
        self.main_window.show()
        self.exec_()
