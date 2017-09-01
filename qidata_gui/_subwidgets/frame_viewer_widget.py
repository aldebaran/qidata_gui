# -*- coding: utf-8 -*-

# Standard libraries
import math
import os
import uuid

# Third-party libraries
import cv2
from image import Image
import numpy
from PySide import QtGui, QtCore
import qidata
from qidata import DataType
from qidata.metadata_objects import Transform

# Local modules
from qidata_gui import RESOURCES_DIR
from .raw_data_display_widgets import makeRawDataWidget
from .raw_data_display_widgets.graphics_elements import Scene, AnnotationItem

class Projected3DROI(QtGui.QGraphicsRectItem, AnnotationItem):
	"""
	Item to show the position of an object on an image.
	"""

	# ──────────
	# Contructor

	def __init__(self, coordinates, plane, info, parent=None):
		"""
		Projected3DROI constructor

		:param coordinates: Object position
		:type coordinates: list
		:param plane: Axis indices of the plane on which the data is projected
		              ("01" for xy, "12" for yz and so on)
		:type plane: str
		:param info: Data represented by this item
		:param parent: Parent of this widget
		:type parent: QtGui.QWidget
		"""
		self.plane = plane
		QtGui.QGraphicsRectItem.__init__(self)
		self.setFlags(QtGui.QGraphicsItem.ItemIsFocusable)
		self.setPen(QtGui.QPen(QtGui.QColor(255,0,0)))
		self.info = info
		self.coordinates = coordinates
		self.parent = parent
		self._refresh()

	# ──────────
	# Public API

	def move(self, d):
		"""
		Move this item

		:param d: Translation to apply
		:type d: QtGui.QPoint
		"""
		dx = int(math.floor(0.5+d.x()))
		dy = int(math.floor(0.5+d.y()))

		h_axis = int(self.plane[0])
		v_axis = int(self.plane[1])

		self.coordinates[0][h_axis] = self.coordinates[0][h_axis] + dx
		self.coordinates[0][v_axis] = self.coordinates[0][v_axis] - dy
		self.coordinates[1][h_axis] = self.coordinates[1][h_axis] + dx
		self.coordinates[1][v_axis] = self.coordinates[1][v_axis] - dy

		self._refresh()

	def increaseSize(self, horizontal, vertical):
		h_axis = int(self.plane[0])
		v_axis = int(self.plane[1])

		self.coordinates[0][h_axis] = self.coordinates[0][h_axis] - horizontal
		self.coordinates[0][v_axis] = self.coordinates[0][v_axis] - vertical
		self.coordinates[1][h_axis] = self.coordinates[1][h_axis] + horizontal
		self.coordinates[1][v_axis] = self.coordinates[1][v_axis] + vertical

		self._refresh()

	# ───────────
	# Private API

	def _refresh(self):
		h_axis = int(self.plane[0])
		v_axis = int(self.plane[1])
		x_min = self.coordinates[0][h_axis]
		y_min = -self.coordinates[1][v_axis]
		x_max = self.coordinates[1][h_axis]
		y_max = -self.coordinates[0][v_axis]

		self.setRect(QtCore.QRect(x_min, y_min, x_max-x_min, y_max-y_min))

class Scene3D(object):
	"""
	Class to handle several scenes representing different views of the same
	3D scene (which cannot be directly represented in Qt4).
	"""

	def __init__(self, parent_widget):
		self.parent_widget = parent_widget
		self.scenes = dict()
		self._item2handle = dict()
		self._handle2items = dict()
		for plane in ["01", "12", "02"]:
			self.scenes[plane] = Scene(self)
			self.scenes[plane].itemAdditionRequested.connect(
			    lambda x: self.parent_widget.itemAdditionRequested.emit(
			        self.parent_widget._locationToCoordinates(x)
			    )
			)
			self.scenes[plane].itemDeletionRequested.connect(self.parent_widget.itemDeletionRequested)
			self.scenes[plane].itemSelected.connect(self.parent_widget.itemSelected)

	# ──────────
	# Properties

	@property
	def read_only(self):
		return self.parent_widget.read_only

	# ──────────
	# Public API

	def add3DPoint(self, coordinates):
		for plane in self.scenes:
			h_axis = int(plane[0])
			v_axis = int(plane[1])
			self.scenes[plane].addRect(
			    coordinates[h_axis]*100,
			    -coordinates[v_axis]*100,
			    1,
			    1,
			    QtGui.QPen(),
			    QtGui.QBrush(QtGui.QColor(0, 0, 0)))

	def addItem(self, location, info):
		handle = str(uuid.uuid4())
		self._handle2items[handle] = []

		for plane in self.scenes:
			item = Projected3DROI(location, plane, info, self)
			self._item2handle[item] = handle
			self._handle2items[handle].append(item)
			self.scenes[plane].addItem(item)

	def clearAllItems(self):
		for plane in self.scenes:
			self.scenes[plane].clearAllItems()
		self._item2handle = dict()
		self._handle2items = dict()

	def removeItem(self, item):
		handle = self._item2handle[item]
		items = self._handle2items.pop(handle)
		for item in items:
			item.scene().removeItem(item)
			self._item2handle.pop(item)

	def __getitem__(self, key):
		return self.scenes[key]

class FrameViewer(QtGui.QWidget):

	itemAdditionRequested = QtCore.Signal(list)
	itemDeletionRequested = QtCore.Signal(list)
	itemSelected = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, files, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.transform_to_files_map = dict()
		self.raw_data_to_files_map = dict()
		self.type_to_files_map = dict()
		self._data_has_tf = False
		self._frame_has_3d = False

		_ref_tf = Transform()

		for file_name in files:
			with qidata.open(file_name) as qidata_file:
				self.transform_to_files_map[file_name] = qidata_file.transform
				self.raw_data_to_files_map[file_name] = qidata_file.raw_data
				self.type_to_files_map[file_name] = qidata_file.type
				self._data_has_tf |= (_ref_tf != qidata_file.transform)
				self._frame_has_3d |= (DataType.IMAGE_3D == qidata_file.type)

		if not self._data_has_tf or not self._frame_has_3d:
			self.main_layout = QtGui.QHBoxLayout(self)
			self.main_widget = QtGui.QSplitter(QtCore.Qt.Vertical, self)
			self.main_layout.addWidget(self.main_widget)
			column_index = 0
			row_index = 0
			self.main_widget.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal, self.main_widget))

			for file_name in files:
				current_row_widget = self.main_widget.widget(row_index)
				current_row_widget.addWidget(
				    makeRawDataWidget(
				        self,
				        self.type_to_files_map[file_name],
				        self.raw_data_to_files_map[file_name]
				    ),
				)
				# Fill cell by cell in a way that the total surface is always as
				# small as possible (well it is actually not optimal, but it does
				# a pretty good job without being too complex)
				# Here is an array showing in which order cells are filled
				# 0  2  6 12
				# 1  3  7 13
				# 4  5  8 14
				# 9 10 11 15

				if row_index == column_index:
					column_index = 0
					row_index += 1
					if self.main_widget.count() == row_index:
						self.main_widget.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal, self.main_widget))
				elif row_index == column_index+1:
					column_index += 1
					row_index = 0
				elif row_index > column_index:
					column_index += 1
				else:
					row_index += 1
					if self.main_widget.count() == row_index:
						self.main_widget.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal, self.main_widget))

		else:
			self.main_layout = QtGui.QVBoxLayout(self)
			self.setLayout(self.main_layout)

			## Buttons bar
			self.buttons_widget = QtGui.QWidget(self)
			self.main_layout.addWidget(self.buttons_widget)

				# "Fit window" button
			self.fit_button = QtGui.QPushButton("", self.buttons_widget)
			fit_ic_path = os.path.join(RESOURCES_DIR, "zoom_fit.png")
			fit_ic = QtGui.QIcon(fit_ic_path)
			self.fit_button.setFixedSize(
			    fit_ic.actualSize(
			        fit_ic.availableSizes()[0]
			    )
			)
			self.fit_button.setText("")
			self.fit_button.setToolTip("Resize image so that it fits the window")
			self.fit_button.setIcon(fit_ic)
			self.fit_button.setIconSize(fit_ic.availableSizes()[0])
			self.fit_button.clicked.connect(self._fitContentToWindow)

			# "XY" button
			self.xy_button = QtGui.QPushButton("xy", self.buttons_widget)
			self.xy_button.setFixedSize(
			    fit_ic.actualSize(
			        fit_ic.availableSizes()[0]
			    )
			)
			self.xy_button.clicked.connect(lambda: self._switchAxis("01"))

			# "XZ" button
			self.xz_button = QtGui.QPushButton("xz", self.buttons_widget)
			self.xz_button.setFixedSize(
			    fit_ic.actualSize(
			        fit_ic.availableSizes()[0]
			    )
			)
			self.xz_button.clicked.connect(lambda: self._switchAxis("02"))

			# "YZ" button
			self.yz_button = QtGui.QPushButton("yz", self.buttons_widget)
			self.yz_button.setFixedSize(
			    fit_ic.actualSize(
			        fit_ic.availableSizes()[0]
			    )
			)
			self.yz_button.clicked.connect(lambda: self._switchAxis("12"))

			# Aggregation
			self.top_layout = QtGui.QHBoxLayout(self)
			self.top_layout.addWidget(self.fit_button)
			self.top_layout.addWidget(self.xy_button)
			self.top_layout.addWidget(self.xz_button)
			self.top_layout.addWidget(self.yz_button)
			self.buttons_widget.setLayout(self.top_layout)

			self.scene = Scene3D(self)
			self.view = QtGui.QGraphicsView(self)
			self.main_layout.addWidget(self.view)
			self.pts_3d = []
			for file_name in self.type_to_files_map:
				if DataType.IMAGE_3D == self.type_to_files_map[file_name]:
					img = Image(file_name)
					pts = [[[a,b]] for b in range(0,img.height) for a in range(0,img.width)]
					# pts = [
					#          [[0,0]], [[1,0]], .., [[W-1,0]],
					#          [[0,1]],     ....,    [[W-1,1]],
					#                       ....,             ,
					#          ...                 [[W-1,H-1]]
					#       ]

					tmp_3d = cv2.undistortPoints(
					             numpy.array(pts,dtype=numpy.float32),
					             numpy.array(img.camera_info.camera_matrix),
					             numpy.array(img.camera_info.distortion_coeffs),
					         )

					h = img.height
					w = img.width
					tmp_3d = tmp_3d.reshape((h, w, 2)).tolist()
					img_data = img.numpy_image
					for u in range(h):
						for v in range(w):
							tmp_3d[u][v][0] *= float(img_data[u][v])/1000
							tmp_3d[u][v][1] *= float(img_data[u][v])/1000
							tmp_3d[u][v].append(float(img_data[u][v])/1000)
							tmp_3d[u][v].append(1) # Put it in "homogeneous" mode

					with qidata.open(file_name) as qidata_image:
						t = transform_matrix(qidata_image.transform)
					for i in range(h):
						for j in range(w):
							pt_3d_cam = tmp_3d[i][j]
							pt_3d_world = numpy.dot(t, numpy.array(pt_3d_cam))
							self.pts_3d.append(pt_3d_world)

			for pt_3d_world in self.pts_3d:
				self.scene.add3DPoint(pt_3d_world)

			self._switchAxis("01")

	# ──────────
	# Decorators

	def skip_if_not_3d(f):
		def wraps(self, *args, **kwargs):
			if self._data_has_tf and self._frame_has_3d:
				return f(self, *args, **kwargs)
			else:
				return None
		return wraps

	# ──────────
	# Properties

	@property
	def read_only(self):
		return self._read_only

	@read_only.setter
	def read_only(self, new_value):
		self._read_only = new_value

	# ──────────
	# Public API

	def addItem(self, location, info):
		self.scene.addItem(location, info)

	@skip_if_not_3d
	def removeItem(self, item):
		self.scene.removeItem(item)

	@skip_if_not_3d
	def selectItem(self, item):
		self.view.scene().selectItem(item)

	def deselectAll(self):
		"""
		De-focus any focused item
		"""
		self.focusOutSelectedItem()

	@skip_if_not_3d
	def focusOutSelectedItem(self):
		self.view.scene().focusOutSelectedItem()

	@skip_if_not_3d
	def clearAllItems(self):
		self.scene.clearAllItems()

	# ───────────
	# Private API

	def _fitContentToWindow(self):
		self.view.fitInView(self.view.scene().sceneRect(),
			                QtCore.Qt.KeepAspectRatio)

	def _switchAxis(self, plane):
		self.scene[plane].refreshItems()
		self.view.setScene(self.scene[plane])
		self.plane = plane

	def _locationToCoordinates(self, location):
		"""
		Create a proper set of coordinates to appropriately represent
		the given location on the data type.
		"""
		h_axis = int(self.plane[0])
		v_axis = int(self.plane[1])
		loc = [0,0,0]
		loc[h_axis] = int(location.x())
		loc[v_axis] = -int(location.y())

		return [[loc[0]-30,loc[1]-30,loc[2]-30],[loc[0]+30,loc[1]+30,loc[2]+30]]

_EPS = numpy.finfo(float).eps * 4.0

def transform_matrix(transform_struct):
    """Return homogeneous rotation matrix from quaternion.

    >>> M = quaternion_matrix([0.99810947, 0.06146124, 0, 0])
    >>> numpy.allclose(M, rotation_matrix(0.123, [1, 0, 0]))
    True
    >>> M = quaternion_matrix([1, 0, 0, 0])
    >>> numpy.allclose(M, numpy.identity(4))
    True
    >>> M = quaternion_matrix([0, 1, 0, 0])
    >>> numpy.allclose(M, numpy.diag([1, -1, -1, 1]))
    True

    """
    quaternion = transform_struct.rotation
    trans = transform_struct.translation
    quat = [quaternion.x, quaternion.y, quaternion.z, quaternion.w]
    q = numpy.array(quat, dtype=numpy.float64, copy=True)
    n = numpy.dot(q, q)
    if n < _EPS:
        return numpy.identity(4)
    q *= math.sqrt(2.0 / n)
    q = numpy.outer(q, q)
    return numpy.array([
        [1.0-q[2, 2]-q[3, 3],     q[1, 2]-q[3, 0],     q[1, 3]+q[2, 0], trans.x],
        [    q[1, 2]+q[3, 0], 1.0-q[1, 1]-q[3, 3],     q[2, 3]-q[1, 0], trans.y],
        [    q[1, 3]-q[2, 0],     q[2, 3]+q[1, 0], 1.0-q[1, 1]-q[2, 2], trans.z],
        [                0.0,                 0.0,                 0.0,     1.0]
    ])