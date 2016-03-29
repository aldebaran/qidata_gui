#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import sys
# PySide
from PySide import QtGui, QtCore

class AnnotatorWindow(QtGui.QMainWindow):
    def __init__(self):
        super(AnnotatorWindow, self).__init__()

        self.printer = QtGui.QPrinter()
        self.scale_factor = 0.0

        self.image_label = QtGui.QLabel()
        self.image_label.setBackgroundRole(QtGui.QPalette.Base)
        self.image_label.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.image_label.setScaledContents(True)

        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setWidget(self.image_label)
        self.setCentralWidget(self.scroll_area)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Viewer")
        self.resize(500, 400)

    def open(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
        if filename:
            image = QtGui.QImage(filename)
            if image.isNull():
                QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % filename)
                return

            self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
            self.scale_factor = 1.0

            self.print_act.setEnabled(True)
            self.fit_to_window_act.setEnabled(True)
            self.updateActions()

            if not self.fit_to_window_act.isChecked():
                self.image_label.adjustSize()

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.image_label.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image_label.pixmap().rect())
            painter.drawPixmap(0, 0, self.image_label.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.image_label.adjustSize()
        self.scale_factor = 1.0

    def fitToWindow(self):
        fit_to_window = self.fit_to_window_act.isChecked()
        self.scroll_area.setWidgetResizable(fit_to_window)
        if not fit_to_window:
            self.normalSize()

        self.updateActions()

    def about(self):
        QtGui.QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.open_act = QtGui.QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.print_act = QtGui.QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.exit_act = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoom_in_act  = QtGui.QAction("Zoom &In (25%)",  self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoom_out_act = QtGui.QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normal_size_act = QtGui.QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fit_to_window_act = QtGui.QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)
        self.about_act = QtGui.QAction("&About", self, triggered=self.about)
        self.about_qt_act = QtGui.QAction("About &Qt", self, triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.file_menu = QtGui.QMenu("&File", self)
        self.file_menu.addAction(self.open_act)
        self.file_menu.addAction(self.print_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_act)

        self.view_menu = QtGui.QMenu("&View", self)
        self.view_menu.addAction(self.zoom_in_act)
        self.view_menu.addAction(self.zoom_out_act)
        self.view_menu.addAction(self.normal_size_act)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.fit_to_window_act)

        self.help_menu = QtGui.QMenu("&Help", self)
        self.help_menu.addAction(self.about_act)
        self.help_menu.addAction(self.about_qt_act)

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.view_menu)
        self.menuBar().addMenu(self.help_menu)

    def updateActions(self):
        self.zoom_in_act.setEnabled(not self.fit_to_window_act.isChecked())
        self.zoom_out_act.setEnabled(not self.fit_to_window_act.isChecked())
        self.normal_size_act.setEnabled(not self.fit_to_window_act.isChecked())

    def scaleImage(self, factor):
        self.scale_factor *= factor
        self.image_label.resize(self.scale_factor * self.image_label.pixmap().size())

        self.adjustScrollBar(self.scroll_area.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scroll_area.verticalScrollBar(), factor)

        self.zoom_in_act.setEnabled(self.scale_factor < 3.0)
        self.zoom_out_act.setEnabled(self.scale_factor > 0.333)

    def adjustScrollBar(self, scrollbar, factor):
        scrollbar.setValue(int(factor * scrollbar.value() + ((factor - 1) * scrollbar.pageStep()/2)))

	def keyPressEvent(self, e):
		print "Received key press event: " + str(e.key())

	def keyReleaseEvent(self, e):
		print "Received key release event: " + str(e.key())
