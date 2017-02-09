# -*- coding: utf-8 -*-

# Standard library
import abc

# Qt
from PySide import QtCore, QtGui

class QtAbstractMetaClass(abc.ABCMeta, type(QtGui.QWidget)): pass

class RawDataWidgetInterface(object):
	"""
	Abstract class. It displays the raw data of a QiDataObject, as well
	as the localized metadata.
	"""
	__metaclass__ = QtAbstractMetaClass

	def __new__(cls, *args, **kwargs):
		"""
		Make sure class has no abstract attributes
		"""
		new_to_use = super(RawDataWidgetInterface, cls).__new__
		if new_to_use.__self__ is not object:
			# next new is not object.__new__
			# test for abstract methods
			if getattr(cls, '__abstractmethods__', None):
				raise TypeError(
				    "Can't instantiate abstract class %s "
				    "with abstract methods %s" % (
				        cls.__name__,
				        ', '.join(sorted(cls.__abstractmethods__))))
		return new_to_use(cls, *args, **kwargs)

	# ───────
	# Signals

	#: User asked for a metadata object to be added at location given in parameter
	objectAdditionRequired = QtCore.Signal(list)

	# ───────
	# Methods

	@abc.abstractmethod
	def addObject(self, coordinates):
		"""
		Add a metadata object to display on the view.

		:param coordinates:  Coordinates of the object to show (format depends on data type)
		:return:  Reference to the widget representing the object

		.. note::
			The returned reference is handy to connect callbacks on the
			widget signals. This reference is also needed to remove the object.
		"""
		return MetadataBaseItem()

	@abc.abstractmethod
	def removeItem(self, item):
		"""
		Remove an object from the widget

		:param item:  Reference to the widget
		"""
		return

	@abc.abstractmethod
	def _locationToCoordinates(self, location):
		"""
		Create a proper set of coordinates to appropriately represent
		the given location on the data type.
		"""
		return None