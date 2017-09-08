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
		self.h_sign = -1 if "-" == plane[0] else 1
		self.h_axis = int(plane[1])
		self.v_sign = -1 if "-" == plane[2] else 1
		self.v_axis = int(plane[3])
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

		self.coordinates[0][self.h_axis] = self.coordinates[0][self.h_axis] + self.h_sign * dx / self.parent.factor
		self.coordinates[0][self.v_axis] = self.coordinates[0][self.v_axis] + self.v_sign * dy / self.parent.factor
		self.coordinates[1][self.h_axis] = self.coordinates[1][self.h_axis] + self.h_sign * dx / self.parent.factor
		self.coordinates[1][self.v_axis] = self.coordinates[1][self.v_axis] + self.v_sign * dy / self.parent.factor

		self._refresh()

	def increaseSize(self, horizontal, vertical):

		# Here the signs of the axis don't matter, as the increase happen
		# symetrically

		self.coordinates[0][self.h_axis] = self.coordinates[0][self.h_axis] - horizontal / self.parent.factor
		self.coordinates[0][self.v_axis] = self.coordinates[0][self.v_axis] - vertical / self.parent.factor
		self.coordinates[1][self.h_axis] = self.coordinates[1][self.h_axis] + horizontal / self.parent.factor
		self.coordinates[1][self.v_axis] = self.coordinates[1][self.v_axis] + vertical / self.parent.factor

		self._refresh()

	# ───────────
	# Private API

	def _refresh(self):

		x_min = min(
		    self.h_sign * int(round(self.parent.factor*self.coordinates[0][self.h_axis])),
		    self.h_sign * int(round(self.parent.factor*self.coordinates[1][self.h_axis]))
		)
		y_min = min(
		    self.v_sign * int(round(self.parent.factor*self.coordinates[0][self.v_axis])),
		    self.v_sign * int(round(self.parent.factor*self.coordinates[1][self.v_axis]))
		)
		x_max = max(
		    self.h_sign * int(round(self.parent.factor*self.coordinates[0][self.h_axis])),
		    self.h_sign * int(round(self.parent.factor*self.coordinates[1][self.h_axis]))
		)
		y_max = max(
		    self.v_sign * int(round(self.parent.factor*self.coordinates[0][self.v_axis])),
		    self.v_sign * int(round(self.parent.factor*self.coordinates[1][self.v_axis]))
		)

		self.setRect(QtCore.QRect(x_min, y_min, x_max-x_min, y_max-y_min))

class PointCloudItem(QtGui.QGraphicsItem):
	def __init__(self, plane, pts, factor):
		QtGui.QGraphicsItem.__init__(self)
		self.pts = pts
		self.factor = factor

		self.h_sign = -1 if "-" == plane[0] else 1
		self.h_axis = int(plane[1])
		self.v_sign = -1 if "-" == plane[2] else 1
		self.v_axis = int(plane[3])

		self.x_min = self.h_sign*int(round(self.factor*self.pts[0][0][self.h_axis]))
		self.y_min = self.v_sign*int(round(self.factor*self.pts[0][0][self.v_axis]))
		self.x_max = self.h_sign*int(round(self.factor*self.pts[0][0][self.h_axis]))
		self.y_max = self.v_sign*int(round(self.factor*self.pts[0][0][self.v_axis]))

		for pt in self.pts:
			if self.x_min > self.h_sign*int(round(self.factor*pt[0][self.h_axis])):
				self.x_min = self.h_sign*int(round(self.factor*pt[0][self.h_axis]))

			if self.y_min > self.v_sign*int(round(self.factor*pt[0][self.v_axis])):
				self.y_min = self.v_sign*int(round(self.factor*pt[0][self.v_axis]))

			if self.x_max < self.h_sign*int(round(self.factor*pt[0][self.h_axis])):
				self.x_max = self.h_sign*int(round(self.factor*pt[0][self.h_axis]))

			if self.y_max < self.v_sign*int(round(self.factor*pt[0][self.v_axis])):
				self.y_max = self.v_sign*int(round(self.factor*pt[0][self.v_axis]))

	def paint(self, painter, option, widget):
		for pt in self.pts:

			if len(pt)>1:
				# Color is BGR, but Qt wants RGB
				color = QtGui.QColor(
				                     pt[1][2],
				                     pt[1][1],
				                     pt[1][0]
				                    )
			else:
				color = QtGui.QColor(0, 0, 0)

			painter.setBrush(QtGui.QBrush(color))
			painter.setPen(QtGui.QPen(color, 1))
			painter.drawRect(
			    self.h_sign*int(round(self.factor*pt[0][self.h_axis])),
			    self.v_sign*int(round(self.factor*pt[0][self.v_axis])),
			    1, 1
			)

	def boundingRect(self):
		return QtCore.QRectF(
		    self.x_min, self.y_min,
		    self.x_max - self.x_min,
		    self.y_max - self.y_min
		)

class Scene3D(object):
	"""
	Class to handle several scenes representing different views of the same
	3D scene (which cannot be directly represented in Qt4).
	"""

	def __init__(self, parent_widget, pt_cloud):
		self.parent_widget = parent_widget
		self.scenes = dict()
		self.pt_cloud = pt_cloud
		self._item2handle = dict()
		self._handle2items = dict()

		# Size factor between the scene and the real world.
		# Basically, the current value transform 1 pixel in the scene in 1 cm
		# in the real world
		self.factor = 100.0

	# ──────────
	# Properties

	@property
	def read_only(self):
		return self.parent_widget.read_only

	# ──────────
	# Public API

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

	def createProjection(self, plane):
		# Create a new scene
		self.scenes[plane] = Scene(self)
		self.scenes[plane].itemAdditionRequested.connect(
		    lambda x: self.parent_widget.itemAdditionRequested.emit(
		        self._locationToCoordinates(x)
		    )
		)
		self.scenes[plane].itemDeletionRequested.connect(self.parent_widget.itemDeletionRequested)
		self.scenes[plane].itemSelected.connect(self.parent_widget.itemSelected)
		self.scenes[plane].setBackgroundBrush(QtCore.Qt.lightGray)

		# Add the 3D point cloud in it
		self._add3DPointCloud(plane, self.pt_cloud)

		# And add every already created items
		for _h in self._handle2items:
			_i = self._handle2items[_h][0]
			item = Projected3DROI(_i.coordinates, plane, _i.info, self)
			self._item2handle[item] = _h
			self._handle2items[_h].append(item)
			self.scenes[plane].addItem(item)

	def removeItem(self, item):
		handle = self._item2handle[item]
		items = self._handle2items.pop(handle)
		for item in items:
			item.scene().removeItem(item)
			self._item2handle.pop(item)

	# ───────────
	# Private API

	def _add3DPointCloud(self, plane, pt_cloud):
		self.scenes[plane].addItem(PointCloudItem(plane, pt_cloud, self.factor))

	def _locationToCoordinates(self, location):
		"""
		Create a proper set of coordinates to appropriately represent
		the given location on the data type.
		"""
		plane = self.parent_widget.plane
		h_sign = -1 if "-" == plane[0] else 1
		h_axis = int(plane[1])
		v_sign = -1 if "-" == plane[2] else 1
		v_axis = int(plane[3])
		loc = [0,0,0]
		loc[h_axis] = h_sign*location.x()/self.factor
		loc[v_axis] = v_sign*location.y()/self.factor

		return [[loc[0]-0.3,loc[1]-0.3,loc[2]-0.3],[loc[0]+0.3,loc[1]+0.3,loc[2]+0.3]]

	def __getitem__(self, key):
		if not self.scenes.has_key(key):
			self.createProjection(key)
		return self.scenes[key]

class FrameViewer(QtGui.QSplitter):

	itemAdditionRequested = QtCore.Signal(list)
	itemDeletionRequested = QtCore.Signal(list)
	itemSelected = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, files, parent=None):
		QtGui.QSplitter.__init__(self, QtCore.Qt.Vertical, parent)
		self.transform_to_files_map = dict()
		self.raw_data_to_files_map = dict()
		self.type_to_files_map = dict()
		self.files_to_type_map = dict()
		self._data_has_tf = False
		self._frame_has_3d = False

		_ref_tf = Transform()

		for file_name in files:
			with qidata.open(file_name) as qidata_file:
				self.transform_to_files_map[file_name] = qidata_file.transform
				self.raw_data_to_files_map[file_name] = qidata_file.raw_data
				self.files_to_type_map[file_name] = qidata_file.type
				if not qidata_file.type in self.type_to_files_map.keys():
					self.type_to_files_map[qidata_file.type] = []
				self.type_to_files_map[qidata_file.type].append(file_name)
				self._data_has_tf |= (_ref_tf != qidata_file.transform)
				self._frame_has_3d |= (DataType.IMAGE_3D == qidata_file.type)


		self._column_index = -1
		self._row_index = -1

		if not self._data_has_tf or not self._frame_has_3d:
			for file_name in files:
				self._addWidget(
				    makeRawDataWidget(
				        None, # parenting will be set at addition
				        self.files_to_type_map[file_name],
				        self.raw_data_to_files_map[file_name]
				    ),
				)

		else:
			self.viewer_widget = QtGui.QWidget(self)
			self._addWidget(self.viewer_widget)
			self.viewer_layout = QtGui.QVBoxLayout(self)
			self.viewer_widget.setLayout(self.viewer_layout)

			## Buttons bar
			self.buttons_widget = QtGui.QWidget(self)
			self.viewer_layout.addWidget(self.buttons_widget)

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
			self.xy_button.clicked.connect(lambda: self._switchAxis("+0-1"))

			# "XZ" button
			self.xz_button = QtGui.QPushButton("xz", self.buttons_widget)
			self.xz_button.setFixedSize(
			    fit_ic.actualSize(
			        fit_ic.availableSizes()[0]
			    )
			)
			self.xz_button.clicked.connect(lambda: self._switchAxis("+0-2"))

			# "YZ" button
			self.yz_button = QtGui.QPushButton("yz", self.buttons_widget)
			self.yz_button.setFixedSize(
			    fit_ic.actualSize(
			        fit_ic.availableSizes()[0]
			    )
			)
			self.yz_button.clicked.connect(lambda: self._switchAxis("-1-2"))

			# Aggregation
			self.top_layout = QtGui.QHBoxLayout(self)
			self.top_layout.addWidget(self.fit_button)
			self.top_layout.addWidget(self.xy_button)
			self.top_layout.addWidget(self.xz_button)
			self.top_layout.addWidget(self.yz_button)
			self.buttons_widget.setLayout(self.top_layout)

			self.view = QtGui.QGraphicsView(self)
			self.viewer_layout.addWidget(self.view)

			self.pts_3d = []
			for file_name in self.type_to_files_map[DataType.IMAGE_3D]:
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
				tmp_3d = tmp_3d.reshape((h, w, 2))
				img_data = img.numpy_image
				tmp_3d = numpy.multiply(tmp_3d,img_data)
				tmp_3d = numpy.append(tmp_3d,img_data, axis=2)
				tmp_3d /= 1000.0
				tmp_3d = numpy.append(tmp_3d, numpy.ones((h,w,1)), axis=2)

				tmp_3d = numpy.transpose(tmp_3d, (2,1,0))
				tmp_3d = numpy.reshape(tmp_3d, (4,h*w))
				# Remove 0 distance points
				tmp_3d = tmp_3d[:,numpy.where(tmp_3d[2,:])[0]]

				with qidata.open(file_name) as qidata_image:
					t = transform_matrix(qidata_image.transform)
				pts_3d_world = numpy.dot(t, tmp_3d)

			color = [[0,0,0]]*h*w

			for file_name in self.type_to_files_map[DataType.IMAGE_2D]:
				img = Image(file_name)
				with qidata.open(file_name) as qidata_image:
					t = transform_matrix(qidata_image.transform)
					t_inv = numpy.linalg.inv(t)

				img_rendered = img.render() # Make sure it is BGR
				m1, m2 = cv2.initUndistortRectifyMap(
				    numpy.array(img.camera_info.camera_matrix),
				    numpy.array(img.camera_info.distortion_coeffs),
				    None,
				    numpy.array(img.camera_info.camera_matrix),
				    (img.width, img.height),
				    cv2.CV_32FC1
				)
				img_rendered_undistort = cv2.remap(img_rendered.numpy_image,m1,m2,cv2.INTER_LINEAR)

				pts_3d_in_cam_frame = numpy.dot(t_inv, pts_3d_world)
				pts_3d_in_cam_plane = numpy.dot(numpy.array(img.camera_info.camera_matrix), pts_3d_in_cam_frame[0:3])
				pts_2d_in_cam_plane = numpy.divide(pts_3d_in_cam_plane[0:2], pts_3d_in_cam_plane[2])
				pts_2d_in_image = pts_2d_in_cam_plane.astype(int)

				for i in range(pts_2d_in_image.shape[1]):
					x = int(pts_2d_in_image[0][i])
					y = int(pts_2d_in_image[1][i])
					if x>=0 and x<img.width and y>=0 and y<img.height:
						color[i] = img_rendered_undistort[y][x].tolist()

			self.pts_3d = numpy.transpose(pts_3d_world).tolist()
			self.pts_3d = zip(self.pts_3d, color)
			self.scene = Scene3D(self, self.pts_3d)

			self._switchAxis("+0-1")

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

	def _addWidget(self, widget):
		# Fill cell by cell in a way that the total surface is always as
		# small as possible (well it is actually not optimal, but it does
		# a pretty good job without being too complex)
		# Here is an array showing in which order cells are filled
		# 0  2  6 12
		# 1  3  7 13
		# 4  5  8 14
		# 9 10 11 15

		if self._row_index == self._column_index:
			self._column_index = 0
			self._row_index += 1
			if self.count() == self._row_index:
				self.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal, self))
		elif self._row_index == self._column_index+1:
			self._column_index += 1
			self._row_index = 0
		elif self._row_index > self._column_index:
			self._column_index += 1
		else:
			self._row_index += 1
			if self.count() == self._row_index:
				self.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal, self))

		current_row_widget = self.widget(self._row_index)
		current_row_widget.addWidget(widget)

	def _fitContentToWindow(self):
		self.view.fitInView(self.view.scene().sceneRect(),
			                QtCore.Qt.KeepAspectRatio)

	def _switchAxis(self, plane):
		self.scene[plane].refreshItems()
		self.view.setScene(self.scene[plane])
		self.plane = plane

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