# -*- coding: utf-8 -*-

# The code defined here is inspired by the graphical interface of Willow
# Garage rqt_bag program, distributed under BSD license.
# BSD license is permissive, but a better check on the conditions might be
# required before totally releasing this program.

# Standard libraries
import bisect
import os

# Third-party libraries
import cv2
from PySide import QtGui, QtCore

# Local modules
from qidata_gui import RESOURCES_DIR

class TimelineItem(QtGui.QGraphicsItem):

	# ───────────
	# Constructor

	def __init__(self, parent, streams):
		"""
		Constructs a QGraphicsItem displaying streams in a timeline

		:param parent: Parent of this item
		:type parent: qidata_gui._subwidgets.StreamViewer
		"""
		super(TimelineItem, self).__init__()
		self._parent = parent

		# Timeline boundries
		self._start_stamp = None  # earliest of all stamps
		self._end_stamp = None  # latest of all stamps
		self._stamp_left = None  # earliest timestamp currently visible
		self._stamp_right = None  # latest timestamp currently visible
		self._history_top = 30
		self._history_left = 0
		self._history_width = 0
		self._history_bottom = 0
		self._margin_left = 4
		self._margin_right = 40
		self._margin_bottom = 20

		# Background Rendering
		self._history_background_color = QtGui.QColor(204, 204, 204, 102)
		self._history_background_color_alternate = QtGui.QColor(179, 179, 179, 25)
		self._history_external_color = QtGui.QColor(0, 0, 0, 25)

		# Timeline Division Rendering
		# Possible time intervals used between divisions
		ms = 0.001
		s = 1
		m = 60
		h = 60*60
		d = 24*60*60
		self._sec_divisions = [
		    1*ms, 5*ms, 10*ms, 50*ms, 100*ms, 500*ms,
		    1*s,  5*s,  15*s,  30*s,
		    1*m,  2*m,  5*m,   10*m,  15*m,   30*m,
		    1*h,  2*h,  3*h,   6*h,   12*h,
		    1*d,  7*d
		]
		self._minor_spacing = 15
		self._major_spacing = 50
		self._major_divisions_label_indent = 3  # padding in px between line and label
		self._major_division_pen = QtGui.QPen(QtGui.QBrush(QtCore.Qt.black),
		                                      0,
		                                      QtCore.Qt.DashLine)
		self._minor_division_pen = QtGui.QPen(QtGui.QBrush(
		                                       QtGui.QColor(153, 153, 153, 128)),
		                                      0,
		                                      QtCore.Qt.DashLine)
		self._minor_division_tick_pen = QtGui.QPen(QtGui.QBrush(
		                                            QtGui.QColor(128, 128, 128, 128)),
		                                           0)

		# Stream Rendering
		self.streams = streams
		self._stream_name_spacing = 3 # min pix between stream name end and history start
		self._stream_font_size = 10.0
		self._stream_font = QtGui.QFont("cairo")
		self._stream_font.setPointSize(self._stream_font_size)
		self._stream_font.setBold(False)
		self._stream_vertical_padding = 4

		# Time Rendering
		self._time_tick_height = 5
		self._time_font_size = 10.0
		self._time_font = QtGui.QFont("cairo")
		self._time_font.setPointSize(self._time_font_size)
		self._time_font.setBold(False)

		# Defaults
		self._default_brush = QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern)
		self._default_pen = QtGui.QPen(QtCore.Qt.black)
		self._default_datatype_color = QtGui.QColor(0, 0, 102, 204)
		self._default_msg_combine_px = 1.0
		# minimum number of pixels allowed between two messages before they are
		# combined
		self._active_message_line_width = 3

		# Current position Rendering
		self._current_pos = None  # timestamp of the current_pos
		self._current_pos_pointer_size = (6, 6)
		self._current_pos_color = QtGui.QColor(255, 0, 0, 191)

	# ──────────
	# Properties

	@property
	def current_pos(self):
		return self._current_pos

	@current_pos.setter
	def current_pos(self, current_pos):
		if current_pos == self._current_pos:
			return

		self._current_pos = current_pos

		if self._current_pos != self._end_stamp:
			self.scene().stick_to_end = False

		self.scene().update()

	# ──────────────────────
	# Override pure virtuals

	def boundingRect(self):
		return QtCore.QRectF(
		    0, 0,
		    self._history_left + self._history_width + self._margin_right,
		    self._history_bottom + self._margin_bottom
		)

	def paint(self, painter, option, widget):
		if self._start_stamp is None:
			return

		self._layout()
		self._draw_stream_dividers(painter)
		self._draw_time_divisions(painter)
		self._draw_stream_histories(painter)
		self._draw_stream_ends(painter)
		self._draw_stream_names(painter)
		self._draw_history_border(painter)
		self._draw_current_pos(painter)

	# ───────────
	# Private API

	def _qfont_width(self, name):
		return QtGui.QFontMetrics(self._stream_font).width(name)

	def _layout(self):
		"""
		Recalculates the layout of the timeline to take into account any changes
		that have occured
		"""
		# Calculate history left and history width
		self._scene_width = self.scene().views()[0].size().width()

		max_stream_name_width = -1
		for stream_name in self.streams:
			stream_width = self._qfont_width(stream_name)
			if max_stream_name_width <= stream_width:
				max_stream_name_width = stream_width

		# Calculate font height for each stream
		self._stream_font_height = -1
		for stream_name in self.streams:
			stream_height = QtGui.QFontMetrics(self._stream_font).height()
			if self._stream_font_height <= stream_height:
				self._stream_font_height = stream_height

		# Update the timeline boundries
		new_history_left = self._margin_left + max_stream_name_width + self._stream_name_spacing
		new_history_width = self._scene_width - new_history_left - self._margin_right
		self._history_left = new_history_left
		self._history_width = new_history_width

		# Calculate the bounds for each stream
		self._history_boundaries = {}
		y = self._history_top
		for stream_name in self.streams:
			stream_height = self._stream_font_height + self._stream_vertical_padding
			self._history_boundaries[stream_name] = (self._history_left,
			                                         y,
			                                         self._history_width,
			                                         stream_height)
			y += stream_height

		new_history_bottom = max([y + h for (_, y, _, h) in self._history_boundaries.values()]) - 1
		if new_history_bottom != self._history_bottom:
			self._history_bottom = new_history_bottom

	def _draw_stream_histories(self, painter):
		"""
		Draw all stream messages

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		for stream in sorted(self._history_boundaries.keys()):
			self._draw_stream_history(painter, stream)

	def _draw_stream_history(self, painter, stream_name):
		"""
		Draw boxes corresponding to message regions on the timeline.

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		:param stream_name: the stream for which message boxes should be drawn
		:type stream_name: str
		"""

		# x, y, w, h = self._history_boundaries[stream]
		_, y, _, h = self._history_boundaries[stream_name]

		msg_y = y
		msg_height = h

		# Get the renderer and the message combine interval
		msg_combine_interval = self.map_dx_to_dstamp(self._default_msg_combine_px)

		# Get the stamps
		all_stamps = self.streams[stream_name].keys()
		all_stamps.sort()
		all_stamps_in_float = map(lambda x: float(x[0])+float(x[1])/1000000000, all_stamps)

		# start_index = bisect.bisect_left(all_stamps, self._stamp_left)
		end_index = bisect.bisect_left(
		                all_stamps_in_float,
		                self._stamp_right
		            )

		# Iterate through regions of connected messages
		width_interval = self._history_width / (self._stamp_right - self._stamp_left)

		# Draw stamps
		grouped_stamps = self._group_close_stamps(
		                     all_stamps_in_float[:end_index],
		                     msg_combine_interval
		                 )

		for (stamp_start, stamp_end) in grouped_stamps:
			if stamp_end < self._stamp_left:
				continue

			region_x_start = self._history_left + (stamp_start - self._stamp_left) * width_interval
			if region_x_start < self._history_left:
				region_x_start = self._history_left  # Clip the region
			region_x_end = self._history_left + (stamp_end - self._stamp_left) * width_interval
			region_width = max(1, region_x_end - region_x_start)

			painter.setBrush(QtGui.QBrush(self._default_datatype_color))
			painter.setPen(QtGui.QPen(self._default_datatype_color, 1))
			painter.drawRect(region_x_start, msg_y, region_width, msg_height)

		# Draw active message
		if self.current_pos is not None:
			curpen = painter.pen()
			oldwidth = curpen.width()
			curpen.setWidth(self._active_message_line_width)
			painter.setPen(curpen)
			current_pos_stamp = None
			current_pos_index = bisect.bisect_right(all_stamps_in_float, self.current_pos) - 1
			if current_pos_index >= 0:
				current_pos_stamp = all_stamps_in_float[current_pos_index]
				if current_pos_stamp > self._stamp_left and current_pos_stamp < self._stamp_right:
					current_pos_x = self._history_left\
					                + (all_stamps_in_float[current_pos_index] - self._stamp_left)\
					                  * width_interval
					painter.drawLine(current_pos_x, msg_y, current_pos_x, msg_y + msg_height)
			curpen.setWidth(oldwidth)
			painter.setPen(curpen)

		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _draw_stream_ends(self, painter):
		"""
		Draw markers to indicate the area covered by all the streams within the
		current visible area.

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		x_start = self.map_stamp_to_x(self._start_stamp)
		x_end = self.map_stamp_to_x(self._end_stamp)
		painter.setBrush(QtGui.QBrush(self._history_external_color))
		painter.drawRect(self._history_left,
		                 self._history_top,
		                 x_start - self._history_left,
		                 self._history_bottom - self._history_top)

		painter.drawRect(x_end,
		                 self._history_top,
		                 self._history_left + self._history_width - x_end,
		                 self._history_bottom - self._history_top)

		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _draw_stream_dividers(self, painter):
		"""
		Draws boxes to separate the different stream lines

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		clip_left = self._history_left
		clip_right = self._history_left + self._history_width

		row = 0
		for stream_name in self.streams:
			(x, y, w, h) = self._history_boundaries[stream_name]

			if row % 2 == 0:
				painter.setPen(QtCore.Qt.lightGray)
				painter.setBrush(QtGui.QBrush(self._history_background_color_alternate))
			else:
				painter.setPen(QtCore.Qt.lightGray)
				painter.setBrush(QtGui.QBrush(self._history_background_color))
			left = max(clip_left, x)
			painter.drawRect(left, y, min(clip_right - left, w), h)
			row += 1
		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _draw_current_pos(self, painter):
		"""
		Draw a line and 2 triangles to denote the current position being viewed

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		if self.current_pos is None:
			return
		px = self.map_stamp_to_x(self.current_pos)
		pw, ph = self._current_pos_pointer_size

		# Line
		painter.setPen(QtGui.QPen(self._current_pos_color))
		painter.setBrush(QtGui.QBrush(self._current_pos_color))
		painter.drawLine(px, self._history_top - 1, px, self._history_bottom + 2)

		# Upper triangle
		py = self._history_top - ph
		painter.drawPolygon(
		    QtGui.QPolygonF(
		        [QtCore.QPointF(px, py + ph),
		         QtCore.QPointF(px + pw, py),
		         QtCore.QPointF(px - pw, py)]
		    )
		)

		# Lower triangle
		py = self._history_bottom + 1
		painter.drawPolygon(
		    QtGui.QPolygonF(
		        [QtCore.QPointF(px, py),
		         QtCore.QPointF(px + pw, py + ph),
		         QtCore.QPointF(px - pw, py + ph)]
		    )
		)

		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _draw_history_border(self, painter):
		"""
		Draw a simple black rectangle frame around the timeline view area

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		x = self._history_left
		y = self._history_top
		w = self._history_width
		h = self._history_bottom - self._history_top

		painter.setBrush(QtCore.Qt.NoBrush)
		painter.setPen(QtCore.Qt.black)
		painter.drawRect(x, y, w, h)
		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _draw_stream_names(self, painter):
		"""
		Calculate positions of existing stream names and draw them on the left,
		one for each row

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		streams = self._history_boundaries.keys()
		coords = [(self._margin_left, y + (h / 2) + (self._stream_font_height / 2))\
		              for (_, y, _, h) in self._history_boundaries.values()]

		for text, coords in zip([t.lstrip('/') for t in streams], coords):
			painter.setBrush(self._default_brush)
			painter.setPen(self._default_pen)
			painter.setFont(self._stream_font)
			painter.drawText(coords[0], coords[1], text)

	def _draw_time_divisions(self, painter):
		"""
		Draw vertical grid-lines showing major and minor time divisions.

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		"""
		x_per_sec = self.map_dstamp_to_dx(1.0)
		major_divisions = [s for s in self._sec_divisions\
		                         if x_per_sec * s >= self._major_spacing]
		if len(major_divisions) == 0:
			major_division = max(self._sec_divisions)
		else:
			major_division = min(major_divisions)

		minor_divisions = [s for s in self._sec_divisions\
		                         if x_per_sec * s >= self._minor_spacing\
		                             and major_division % s == 0]
		if len(minor_divisions) > 0:
			minor_division = min(minor_divisions)
		else:
			minor_division = None

		start_stamp = self._start_stamp

		major_stamps = list(self._get_stamps(start_stamp, major_division))
		self._draw_major_divisions(painter, major_stamps, start_stamp, major_division)

		if minor_division:
			minor_stamps = [s for s in self._get_stamps(start_stamp, minor_division)\
			                      if s not in major_stamps]
			self._draw_minor_divisions(painter,
			                           minor_stamps,
			                           start_stamp,
			                           minor_division)

	def _draw_major_divisions(self, painter, stamps, start_stamp, division):
		"""
		Draw black hashed vertical grid-lines showing major time divisions.

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		:param stamps: Timestamps to display on the view
		:type stamps: list
		:param start_stamp: Timestamp used as time origin (becomes the 0.0000)
		:type start_stamp: float
		:param division: Number of seconds in a division
		:type division: int
		"""
		label_y = self._history_top - self._current_pos_pointer_size[1] - 5
		for stamp in stamps:
			x = self.map_stamp_to_x(stamp, False)

			label = self._get_label(division, stamp - start_stamp)
			label_x = x + self._major_divisions_label_indent
			# This check seems to always hide the date... If a problem occurs
			# this might be reworked to provide a solution, but for now it is
			# more a problem than a solution. the second line is a possible
			# solution
			# if label_x + self._qfont_width(label) < self.scene().width():
			# if label_x + self._qfont_width(label) < self._history_width:
			painter.setBrush(self._default_brush)
			painter.setPen(self._default_pen)
			painter.setFont(self._time_font)
			painter.drawText(label_x, label_y, label)

			painter.setPen(self._major_division_pen)
			painter.drawLine(x, label_y - self._time_tick_height - self._time_font_size,
			                 x, self._history_bottom)

		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _draw_minor_divisions(self, painter, stamps, start_stamp, division):
		"""
		Draw grey hashed vertical grid-lines showing minor time divisions.

		:param painter: allows access to paint functions
		:type painter: QtGui.QPainter
		:param stamps: Timestamps to display on the view
		:type stamps: list
		:param start_stamp: Timestamp used as time origin (becomes the 0.0000)
		:type start_stamp: float
		:param division: Number of seconds in a division
		:type division: int
		"""
		xs = [self.map_stamp_to_x(stamp) for stamp in stamps]
		painter.setPen(self._minor_division_pen)
		for x in xs:
			painter.drawLine(x, self._history_top, x, self._history_bottom)

		painter.setPen(self._minor_division_tick_pen)
		for x in xs:
			painter.drawLine(
			    x, self._history_top - self._time_tick_height,
			    x, self._history_top
			)

		painter.setBrush(self._default_brush)
		painter.setPen(self._default_pen)

	def _group_close_stamps(self, stamps, max_interval):
		"""
		Group timestamps closer from each other than `max_interval` into one
		region

		:param stamps: list of stamps to analyze
		:type stamps: list
		:param max_interval: seconds between each division
		:type max_interval: int
		"""
		region_start, prev_stamp = None, None
		for stamp in stamps:
			if prev_stamp:
				if stamp - prev_stamp > max_interval:
					region_end = prev_stamp
					yield (region_start, region_end)
					region_start = stamp
			else:
				region_start = stamp

			prev_stamp = stamp

		if region_start and prev_stamp:
			yield (region_start, prev_stamp)

	def _get_stamps(self, start_stamp, stamp_step):
		"""
		Generate visible stamps every `stamp_step`

		:param start_stamp: beginning of timeline stamp
		:type start_stamp: int
		:param stamp_step: seconds between each division
		:type stamp_step: int
		"""
		if start_stamp >= self._stamp_left:
			stamp = start_stamp
		else:
			stamp = start_stamp\
			        + int((self._stamp_left - start_stamp) / stamp_step)\
			          * stamp_step\
			        + stamp_step

		while stamp < self._end_stamp:
			yield stamp
			stamp += stamp_step

	def _get_label(self, division, elapsed):
		"""
		Generates a label representing the elapsed time

		:param division: number of seconds in a division
		:type division: int
		:param elapsed: seconds from the beginning
		:type elapsed: int
		:returns: relevant time elapsed string
		:rtype: str
		"""
		secs = int(elapsed) % 60

		mins = int(elapsed) / 60
		hrs = mins / 60
		days = hrs / 24
		weeks = days / 7

		if division >= 7 * 24 * 60 * 60:  # >1wk divisions: show weeks
			return '%dw' % weeks
		elif division >= 24 * 60 * 60:  # >24h divisions: show days
			return '%dd' % days
		elif division >= 60 * 60:  # >1h divisions: show hours
			return '%dh' % hrs
		elif division >= 5 * 60:  # >5m divisions: show minutes
			return '%dm' % mins
		elif division >= 1:  # >1s divisions: show minutes:seconds
			return '%dm%02ds' % (mins, secs)
		elif division >= 0.1:  # >0.1s divisions: show seconds.0
			return '%d.%ss' % (secs, str(int(10.0 * (elapsed - int(elapsed)))))
		elif division >= 0.01:  # >0.1s divisions: show seconds.0
			return '%d.%02ds' % (secs, int(100.0 * (elapsed - int(elapsed))))
		else:  # show seconds.00
			return '%d.%03ds' % (secs, int(1000.0 * (elapsed - int(elapsed))))

	# Pixel location/time conversion functions
	def map_x_to_stamp(self, x, clamp_to_visible=True):
		"""
		Converts a pixel x value to a stamp

		:param x: pixel value to be converted
		:type x: int
		:param clamp_to_visible: disallow values that are greater than the
		                         current timeline bounds
		:type clamp_to_visible: bool
		:returns: timestamp
		:rtype: int
		"""
		fraction = float(x - self._history_left) / self._history_width

		if clamp_to_visible:
			if fraction <= 0.0:
				return self._stamp_left
			elif fraction >= 1.0:
				return self._stamp_right

		return self._stamp_left + fraction * (self._stamp_right - self._stamp_left)

	def map_dx_to_dstamp(self, dx):
		"""
		Converts a distance in pixel space to a distance in stamp space

		:param dx: distance in pixel space to be converted
		:type dx: int
		:returns: distance in stamp space
		:rtype: float
		"""
		return float(dx) * (self._stamp_right - self._stamp_left) / self._history_width

	def map_stamp_to_x(self, stamp, clamp_to_visible=True):
		"""
		Converts a timestamp to the x value where that stamp exists in the
		timeline

		:param stamp: timestamp to be converted
		:type: int
		:param clamp_to_visible: disallow values that are greater than the
		                         current timeline bounds
		:type: bool
		:returns: # of pixels from the left boarder
		:rtype: int
		"""
		if self._stamp_left is None:
			return None
		fraction = (stamp - self._stamp_left) / (self._stamp_right - self._stamp_left)

		if clamp_to_visible:
			fraction = min(1.0, max(0.0, fraction))

		return self._history_left + fraction * self._history_width

	def map_dstamp_to_dx(self, dstamp):
		"""
		Converts a distance in pixel space to a distance in stamp space

		:param dstamp: distance in stamp space to be converted
		:type dx: float
		:returns: distance in pixel space
		:rtype: float
		"""
		return (float(dstamp) * self._history_width) / (self._stamp_right - self._stamp_left)

	def _moveCurrentPosTo(self, pos):
		x = pos.x()
		y = pos.y()
		if x >= self._history_left and x <= self._history_left+self._history_width:
			if y >= self._history_top and y <= self._history_bottom:
				# Clicked within timeline - set current_pos
				current_pos = self.map_x_to_stamp(x)
				if current_pos <= 0.0:
					self.current_pos = self._start_stamp
				else:
					self.current_pos = current_pos
				self.scene().update()

	# ─────
	# Slots

	def mousePressEvent(self, event):
		event.accept()
		self._moveCurrentPosTo(event.pos())

	def mouseMoveEvent(self, event):
		event.accept()
		self._moveCurrentPosTo(event.pos())

	def mouseReleaseEvent(self, event):
		event.accept()
		self._moveCurrentPosTo(event.pos())

		self._parent.objectSelected.emit(
		    self._parent.getFileAtStamp(self.current_pos)
		)

class StreamViewer(QtGui.QWidget):

	objectSelected = QtCore.Signal(list)

	# ───────────
	# Constructor

	def __init__(self, streams, parent=None):
		"""
		Constructs a widget displaying data streams.

		:param streams: Map containing the streams
		:type streams: dict
		:param parent: Parent of this widget
		:type parent: QtGui.QWidget
		"""

		# Initialize class
		QtGui.QWidget.__init__(self, parent)
		self.main_layout = QtGui.QVBoxLayout(self)
		self.setLayout(self.main_layout)

		# Retrieve first and last timestamps
		_streams_ts_float = dict()
		for stream_name in streams.keys():
			tuple_ts = streams[stream_name].keys()
			float_ts = map(lambda x: float(x[0]) + float(x[1])/1000000000, tuple_ts)
			_streams_ts_float[stream_name] = float_ts
			_streams_ts_float[stream_name].sort()

		self.streams = streams
		self.stamps_by_stream = _streams_ts_float

		_start = min([x[0] for x in _streams_ts_float.values()])
		_end = max([x[-1] for x in _streams_ts_float.values()])+1

		# Create view and set view alignment
		self.view = QtGui.QGraphicsView()
		self.main_layout.addWidget(self.view)
		self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

		# Create scene
		self._scene = QtGui.QGraphicsScene()
		self._scene.setBackgroundBrush(QtCore.Qt.white)
		self.view.setScene(self._scene)

		# Create timeline item
		self._timeline = TimelineItem(self, streams)
		self._scene.addItem(self._timeline)
		self._timeline.setPos(0, 0)

			# For now, all the timeline is always visible, but this might
			# change in the future, hence the "left" and "right" stamps
		self._timeline._start_stamp = self._timeline._stamp_left = _start
		self._timeline._end_stamp = self._timeline._stamp_right = _end

		# Create buttons to navigate between frames
		self.buttons_widget = QtGui.QWidget(self)
		self.main_layout.addWidget(self.buttons_widget)
		self.buttons_layout = QtGui.QHBoxLayout(self.buttons_widget)
		self.buttons_widget.setLayout(self.buttons_layout)

		self.previous_button = QtGui.QPushButton("", self.buttons_widget)
		self.buttons_layout.addWidget(self.previous_button)
		self.previous_button.setToolTip("Open previous frame")
		prev_ic_path = os.path.join(RESOURCES_DIR, "resultset_previous.png")
		prev_ic = QtGui.QIcon(prev_ic_path)
		self.previous_button.setIcon(prev_ic)
		self.previous_button.setIconSize(prev_ic.availableSizes()[0])
		self.previous_button.setFixedSize(
		    prev_ic.actualSize(
		        prev_ic.availableSizes()[0]
		    )
		)

		self.next_button = QtGui.QPushButton("", self.buttons_widget)
		self.buttons_layout.addWidget(self.next_button)
		self.next_button.setToolTip("Open next frame")
		next_ic_path = os.path.join(RESOURCES_DIR, "resultset_next.png")
		next_ic = QtGui.QIcon(next_ic_path)
		self.next_button.setIcon(next_ic)
		self.next_button.setIconSize(next_ic.availableSizes()[0])
		self.next_button.setFixedSize(
		    next_ic.actualSize(
		        next_ic.availableSizes()[0]
		    )
		)

		self.previous_button.clicked.connect(self.moveToPreviousFrame)
		self.next_button.clicked.connect(self.moveToNextFrame)

	# ──────────
	# Public API

	def getFileAtStamp(self, timestamp):
		"""
		Return the latest file activated at a specific timestamp

		:param timestamp: Time where we want to know the active file
		:type timestamp: float
		:return: the latest activated file
		:rtype: str
		"""
		out = ""
		out_ts = (0,0)
		for stream_name in self.stamps_by_stream.keys():
			ts_index = bisect.bisect_right(self.stamps_by_stream[stream_name], timestamp)-1
			if ts_index < 0:
				continue
			tuple_ts = self.streams[stream_name].keys()
			tuple_ts.sort()
			if tuple_ts[ts_index] > out_ts:
				out_ts = tuple_ts[ts_index]
				out = self.streams[stream_name][tuple_ts[ts_index]]
		return out

	def getFilesAtStamp(self, timestamp):
		"""
		Return the list of files active at a specific timestamp

		:param timestamp: Time where we want to know the active files
		:type timestamp: float
		:return: list of active files
		:rtype: list
		"""
		out = []
		for stream_name in self.stamps_by_stream.keys():
			ts_index = bisect.bisect_right(self.stamps_by_stream[stream_name], timestamp)-1
			if ts_index < 0:
				continue
			tuple_ts = self.streams[stream_name].keys()
			tuple_ts.sort()
			out.append(self.streams[stream_name][tuple_ts[ts_index]])
		return out

	def moveToPreviousFrame(self):
		"""
		Slides the cursor to the previous frame. Does nothing if there is no
		frame before the current position
		"""
		all_ts = [s for t in self.stamps_by_stream.values() for s in t]
		all_ts.sort()
		first_frame = all_ts[0]

		selected_index = bisect.bisect_right(all_ts, self._timeline.current_pos)-1
		if selected_index <= 0 or all_ts[selected_index-1] < first_frame:
			# There is no data before, or no frame. Do nothing
			return
		self._timeline.current_pos = all_ts[selected_index-1]
		self.objectSelected.emit(
		    self.getFileAtStamp(self._timeline.current_pos)
		)

	def moveToNextFrame(self):
		"""
		Slides the cursor to the next frame. Does nothing if there is no frame
		after the current position
		"""
		all_ts = [s for t in self.stamps_by_stream.values() for s in t]
		all_ts.sort()
		first_frame = all_ts[0]

		selected_index = bisect.bisect_right(all_ts, self._timeline.current_pos)-1
		if len(all_ts)-1 == selected_index:
			# We are already at the last frame
			return

		# Move forward enough to be sure to reach the first frame
		increase = 1
		while all_ts[selected_index+increase] < first_frame:
			increase += 1

		self._timeline.current_pos = all_ts[selected_index+increase]
		self.objectSelected.emit(
		    self.getFileAtStamp(self._timeline.current_pos)
		)

	# ─────
	# Slots

	def closeEvent(self, event):
		event.accept()
