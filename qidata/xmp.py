# -*- coding: utf-8 -*-

# Standard Library
import collections
from compiler.misc import mangle
from itertools import islice
import os.path
import re
import warnings
import weakref
# XMP
import libxmp

ALDEBARAN_NS_V1=u"http://aldebaran.com/xmp/1"
ALDEBARAN_NS = ALDEBARAN_NS_V1
SUGGESTED_ALDEBARAN_NS_PREFIX=u"aldebaran"
libxmp.exempi.register_namespace(ALDEBARAN_NS, SUGGESTED_ALDEBARAN_NS_PREFIX)

# ────────────────────────────────
# libxmp insertion monkey-patching

class CONSTANTS:
	kXMP_InsertBeforeItem = 0x00004000L
	kXMP_InsertAfterItem  = 0x00008000L

if CONSTANTS.kXMP_InsertBeforeItem in libxmp.consts.XMP_PROP_OPTIONS.values():
	warnings.warn("Constant kXMP_InsertBeforeItem has been defined by libxmp in a new version", RuntimeWarning)
if CONSTANTS.kXMP_InsertAfterItem  in libxmp.consts.XMP_PROP_OPTIONS.values():
	warnings.warn("Constant kXMP_InsertAfterItem has been defined by libxmp in a new version", RuntimeWarning)

libxmp.consts.prop_array_insert_before = CONSTANTS.kXMP_InsertBeforeItem
libxmp.consts.prop_array_insert_after  = CONSTANTS.kXMP_InsertAfterItem
libxmp.consts.XMP_PROP_OPTIONS["prop_array_insert_before"] = CONSTANTS.kXMP_InsertBeforeItem
libxmp.consts.XMP_PROP_OPTIONS["prop_array_insert_after"]  = CONSTANTS.kXMP_InsertAfterItem

# ─────────────────────
# Formatting parameters

INDENT_SIZE = 5
INDENT = ' ' * INDENT_SIZE
TREE_INDENT = u'─'*(INDENT_SIZE-2) + " "
TREE_MID_INDENT  = u"├" + TREE_INDENT
TREE_LAST_INDENT = u"└" + TREE_INDENT

# ───────────────
# General XMP API

def isQualified(name):
	return name.find(':') != -1

def qualify(name, prefix):
	return "{prefix}:{name}".format(name=name, prefix=prefix)

class XMPFile(object):
	"""
	Handle to a file path to manipulate as a container to an XMP packet.

	Attributes:
		rw: Whether the file is considered writable.
		file_path: Path to the file to manipulate.
		metadata: The metadata manipulator for the file.
	"""

	def __init__(self, file_path, rw = False):
		self.__rw             = rw
		self.file_path        = os.path.abspath(file_path)
		self.libxmp_file      = None
		self._libxmp_metadata = None
		self.metadata         = None

	# ──────────
	# Properties

	@property
	def libxmp_metadata(self):
		return self._libxmp_metadata

	@libxmp_metadata.setter
	def libxmp_metadata(self, new_metadata):
		if new_metadata is not None:
			self._libxmp_metadata = new_metadata
		else:
			self._libxmp_metadata = libxmp.XMPMeta()
		self.metadata = XMPMetadata(self._libxmp_metadata)

		# Record to warn the user when they modify their metadata in read-only mode
		self.__original_repr = repr(self._libxmp_metadata)

	@property
	def rw(self):
	    return self.__rw

	@property
	def is_open(self):
	    return self.libxmp_file      is not None \
	       and self._libxmp_metadata is not None \
	       and self.metadata         is not None

	@property
	def has_changed(self):
	    return repr(self._libxmp_metadata) != self.__original_repr

	@property
	def read_only(self):
	    return not self.rw

	# ───────────
	# General API

	def open(self):
		if self.is_open:
			warnings.warn("File {} is already open".format(self.file_path), RuntimeWarning)
		if libxmp.exempi.files_check_file_format(self.file_path) == libxmp.consts.XMP_FT_UNKNOWN:
			raise RuntimeError("Unknown XMP file type")

		self.libxmp_file = libxmp.XMPFiles(file_path = self.file_path,
		                                open_onlyxmp = True,
		                              open_forupdate = self.rw)
		self.libxmp_metadata = self.libxmp_file.get_xmp()

	def close(self):
		if not self.is_open:
			warnings.warn("File {} is already closed".format(self.file_path), RuntimeWarning)
			return
		try:
			if self.read_only and self.has_changed:
				message =  "Modified a read-only XMP file; won't be saved"
				warnings.warn(message, RuntimeWarning)

			if self.rw:
				try:
					if self.libxmp_file.can_put_xmp(self.libxmp_metadata):
						self.libxmp_file.put_xmp(self.libxmp_metadata)
					else:
						raise
				except:
					raise RuntimeError("Can't serialize XMP to file " + self.file_path)

		finally:
			self.libxmp_file.close_file()
			self._reset()

	# ───────────────
	# Context Manager

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, type, value, traceback):
		self.close()

	# ───────
	# Helpers

	def _reset(self):
		self.libxmp_file      = None
		self._libxmp_metadata = None
		self.metadata         = None
		self.__original_repr  = None

	# ──────────────
	# Textualization

	def __str__(self):
		return "XMP file {}:\n{}".format(self.file_path, str(self.metadata))

class XMPMetadata(collections.Mapping):
	"""
	XMP metadata packet.

	This may be a purely in-memory packet, or a packet read from a file by an
	XMPFile object managing it and which may automatically write it when closed.
	"""

	def __init__(self, libxmp_metadata = libxmp.XMPMeta()):
		self.libxmp_metadata = libxmp_metadata
		self._namespaces = collections.OrderedDict()

		# Group all elements by namespace and parse them in LibXMPElements
		elements_by_namespace = {}
		for libxmp_tuple in self.libxmp_metadata:
			libxmp_element = LibXMPElement(libxmp_tuple)
			if libxmp_element.is_namespace: continue
			try:
				elements_by_namespace[libxmp_element.namespace].append(libxmp_element)
			except KeyError:
				elements_by_namespace[libxmp_element.namespace] = [libxmp_element]

		# Construct namespaces; each one is the root object of an XMP object tree
		for ns_uid, ns_libxmp_descendents in elements_by_namespace.iteritems():
			namespace = XMPNamespace(self, ns_uid)
			libxmp_members = namespace.childrenIn(ns_libxmp_descendents)
			members = [XMPElement.fromLibXMP(m, ns_libxmp_descendents, namespace)
			           for m in libxmp_members]
			namespace.children = members
			self._namespaces[ns_uid] = namespace

	# ──────────
	# Properties

	@property
	def namespaces(self):
		return [n for n in self]

	# ───────────
	# Mapping API

	def __len__(self):
		return sum(1 for n in self)

	def __iter__(self):
		return (n for n in self._namespaces.itervalues() if n)

	def __getitem__(self, key):
		try:
			return self._namespaces[key]
		except KeyError:
			# If the namespace doesn't exist, create it
			self._namespaces[key] = XMPNamespace(self, key)
			return self._namespaces[key]

	def __setitem__(self, key, value):
		if not isinstance(value, XMPNamespace):
			raise TypeError("XMPMetadata can only set namespaces with XMPNamespace type; given " + str(type(value)))
		self._namespaces[key] = value

	def __delitem__(self, key):
		self._namespaces[key].delete()

	def __contains__(self, uid):
		return uid in self._namespaces and self._namespaces[uid]

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return "\n".join([unicode(n) for n in self.namespaces])

	def pretty_str(self):
		import libxmp.utils
		raw_pretty_string = XMPMetadata.textualizeXMPDict(libxmp.utils.object_to_dict(self.libxmp_metadata))
		return raw_pretty_string.encode("utf-8")

	def xml(self):
		raw_xml = self.libxmp_metadata.serialize_and_format().encode("utf-8")
		return raw_xml

	# ───────
	# Helpers

	@staticmethod
	def textualizeXMPDict(x, indent = ""):
		rep = ""
		if isinstance(x, dict):
			textualized_items = [str(k)+": " + XMPMetadata.textualizeXMPDict(v, indent+' '*(2+len(str(k))))
			                     for k,v in x.iteritems()]
			rep += ("\n"+indent).join(textualized_items)
		elif isinstance(x, list):
			rep += ("\n"+indent).join([u"⁃ " + XMPMetadata.textualizeXMPDict(e, indent+' '*2) for e in x])
		elif isinstance(x, tuple) and len(x) == 3:
			node_name  = x[0]
			node_value = x[1]
			rep += node_name + " = " + node_value
		else:
			return str(x)
		return rep

class TreePredicatesMixin:
	"""
	Defines tree operations for any element that has a namespace and address.
	"""

	ARRAY_ELEMENT_REGEX = re.compile(r"(.*)\[(\d+)\]$")
	INDEX_REGEX = re.compile(r"^\[\d+\]$")
	STRUCT_CHILD_REGEX = re.compile(r"^/[^/]+$")

	# ──────────
	# Properties

	@property
	def name(self):
		return self.address.split("/")[-1]

	@property
	def namespace_uid(self):
		if isinstance(self, LibXMPElement):
			return self.namespace
		elif isinstance(self, XMPElement):
			return self.namespace.uid

	@property
	def is_top_level(self):
		return "/" not in self.address \
		   and not TreePredicatesMixin.ARRAY_ELEMENT_REGEX.match(self.address)

	@property
	def is_array_element(self):
		return TreePredicatesMixin.ARRAY_ELEMENT_REGEX.match(self.address) is not None

	@property
	def parent_address(self):
		if self.is_top_level:
			return None

		if self.is_array_element:
			return TreePredicatesMixin.ARRAY_ELEMENT_REGEX.match(self.address).group(1)
		else:
			return "/".join(self.address.split("/")[:-1])

	@property
	def index(self):
		array_pattern_match = TreePredicatesMixin.ARRAY_ELEMENT_REGEX.match(self.address)
		if not array_pattern_match:
			raise ValueError("Not an array element; please check this is an array element before getting its index")
		return int(array_pattern_match.group(2))

	# ────────────────────
	# Address manipulation

	def absoluteAddress(self, relative_address):
		if not self.address:
			# Relative to a namespace: absolute is relative
			return relative_address
		elif TreePredicatesMixin.INDEX_REGEX.match(relative_address):
			return self.address + relative_address
		else:
			return "{base_address}/{relative_address}".format(base_address = self.address,
			                                              relative_address = relative_address)

	# ──────────
	# Predicates

	def inSameNamespace(self, other):
		return self.namespace_uid == other.namespace_uid

	def isDescendantOf(self, other):
		return self.address.startswith(other.address) \
		   and self.inSameNamespace(other) \
		   and self.address != other.address

	def isAncestorOf(self, other):
		return other.isDescendantOf(self)

	def isChildrenOf(self, other):

		if not self.inSameNamespace(other) \
		or not self.address.startswith(other.address):
			return False

		address_delta = self.address[len(other.address):]
		struct_depth_delta = address_delta.count("/")
		is_array_element = TreePredicatesMixin.ARRAY_ELEMENT_REGEX.match(address_delta) is not None
		other_is_namespace = not other.address

		if other_is_namespace and not is_array_element:
			# If other is a namespace, its address is the empty string and
			# children don't have a / in their address
			return struct_depth_delta == 0
		elif is_array_element:
			return bool(TreePredicatesMixin.INDEX_REGEX.match(address_delta))
		else:
			return bool(TreePredicatesMixin.STRUCT_CHILD_REGEX.match(address_delta))

	def isParentOf(self, other):
		return other.isChildrenOf(self)

	# ─────────────────────────────────
	# Filters in containers of elements

	def descendentsIn(self, elements):
		return [e for e in elements if e.isDescendantOf(self)]

	def ancestorsIn(self, elements):
		return [e for e in elements if e.isAncestorOf(self)]

	def childrenIn(self, elements):
		return [e for e in elements if e.isChildrenOf(self)]

	def parentsIn(self, elements):
		return [e for e in elements if e.isParentOf(self)]

	# ──────────────────
	# Equality operators

	def __eq__(self, other):
		return isinstance(other, self.__class__) \
		   and self.namespace == other.namespace \
		   and self.address   == other.address

	def __neq__(self, other):
		return not self.__eq__(other)

class TreeManipulationMixin(TreePredicatesMixin):
	# ──────────
	# Properties

	@property
	def parent(self):
		parent_address = self.parent_address
		if parent_address is not None:
			return self.namespace[parent_address]
		elif isinstance(self, XMPNamespace):
			return None
		else:
			return self.namespace

class LibXMPElement(object, TreePredicatesMixin):
	""" Wrapper around a libXMP iterator element. """

	# ───────────
	# Constructor

	def __init__(self, tuple):
		self.namespace  = unicode(tuple[0])
		self.address    = unicode(tuple[1])
		self.value      = unicode(tuple[2])
		self.descriptor = tuple[3]

	# ──────────
	# Properties

	@property
	def tuple(self):
		return (self.namespace, self.address, self.value, self.descriptor)

	@property
	def is_container(self):
	    return self.descriptor["VALUE_IS_STRUCT"] or self.descriptor["VALUE_IS_ARRAY"]

	@property
	def is_value(self):
	    return not self.is_container

	@property
	def is_namespace(self):
	    return self.descriptor["IS_SCHEMA"]

	@property
	def is_struct(self):
	    return self.descriptor["VALUE_IS_STRUCT"]

	@property
	def is_array(self):
	    return self.descriptor["VALUE_IS_ARRAY"] and self.descriptor["ARRAY_IS_ORDERED"]

	@property
	def is_set(self):
	    return self.descriptor["VALUE_IS_ARRAY"] and not self.descriptor["ARRAY_IS_ORDERED"]

	# ──────────────
	# Textualization

	def __repr__(self):
		return repr(self.tuple)

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		rep = self.address
		if self.value: rep += " = " + self.value
		return rep

class FreezeMixin:
	@staticmethod
	def marker(classname):
		return "_{classname}___frozen".format(classname = classname)

	@property
	def frozen(self):
		try:
			# Don't use getattr, as the class probably overrides it and tests
			# this function to check whether it should return something special,
			# which would cause an infinite recursion.
			return self.__dict__[FreezeMixin.marker(self.__class__.__name__)]
		except KeyError:
			return False

	def freeze(self, class_or_classname, value = True):
		if isinstance(class_or_classname, str):
			classname = class_or_classname
		elif isinstance(class_or_classname, type):
			classname = class_or_classname.__name__
		else:
			raise ValueError("Freezing is done for a class or class-name")
		# Bypass the objet's setattr, which may have additional semantics
		object.__setattr__(self, FreezeMixin.marker(classname), value)

	def __raw_getattr__(self, name):
		# Search in the object, then in all parent classes if not found
		for o in [self] + self.__class__.mro():
			try:
				return o.__dict__[name]
			except KeyError:
				continue
		raise AttributeError

	def __raw_hasattr__(self, name):
		try:
			self.__raw_getattr__(name)
			return True
		except AttributeError:
			return False

class ContainerMixin:
	def iterchildren(self):
		""" Iterator over children with mutable semantics; must be overriden. """
		raise NotImplementedError("Must be overriden")

	# ────────────────────
	# XMPElement overrides

	@property
	def is_container(self):
		return True

class XMPElement(object, TreeManipulationMixin, FreezeMixin):
	"""
	Manipulator for an element in an XMP packet.

	Abstracts a fully-qualified, absolute address in a namespace of an XMP metadata
	packet. Contrary to :class:`XMPVirtualElement`, the manipulated element already
	exists in the XMP tree.
	"""

	# ────────────
	# Constructors

	def __init__(self, namespace, address):
		"""
		Constructs a manipulator for an XMP element in an XMP packet.

		Arguments:
		    namespace: The namespace to which the element belongs to, or None if the
		               element is a namespace itself. No "strong" reference of it will
		               be kept, only a weakref.
		    address: The fully-qualified, absolute address of the element in its namespace.
		"""

		if namespace is not None and not isinstance(namespace, weakref.ReferenceType):
			self._namespace = weakref.ref(namespace)
		else:
			self._namespace = namespace
		self.address = address
		self.freeze(XMPElement)

	@staticmethod
	def fromLibXMP(libxmp_element, potential_descendents, namespace):
		if libxmp_element.is_value:
			return XMPValue(namespace, libxmp_element.address)
		else:
			# Container type elements
			libxmp_descendents = libxmp_element.descendentsIn(potential_descendents)
			libxmp_children    = libxmp_element.childrenIn(libxmp_descendents)

			# Recursively build children
			children_elements = [XMPElement.fromLibXMP(libxmp_child,
			                                           libxmp_descendents,
			                                           namespace) for libxmp_child \
			                                                       in libxmp_children]

			# Return the assembled tree
			if libxmp_element.is_struct:
				return XMPStructure(namespace, libxmp_element.address, children_elements)
			elif libxmp_element.is_array:
				return XMPArray(namespace, libxmp_element.address, children_elements)
			elif libxmp_element.is_set:
				return XMPSet(namespace, libxmp_element.address, children_elements)

	@staticmethod
	def fromValue(namespace, address, value):
		if isinstance(value, basestring):
			# basestrings are also collections.Sequence, so we cna't put this case in the
			# else case
			return XMPValue(namespace, address)
		elif isinstance(value, collections.Mapping):
			return XMPStructure(namespace, address, [])
		elif isinstance(value, collections.Sequence):
			return XMPArray(namespace, address, [])
		elif isinstance(value, collections.Set):
			return XMPSet(namespace, address, [])
		else:
			return XMPValue(namespace, address)

	# ────────
	# CRUD API

	# Warning: This API removes things from the XMP packet without doing the
	# associated book-keeping in the object tree.

	def _create(self, value = None):
		"""
		Creates an element given that its parent already has been created.

		Arguments
			value: the value to initialize the element with (by default None)
		"""
		raise NotImplementedError("Must be overriden")

	@property
	def value(self):
		raise NotImplementedError("Must be overriden")

	def update(self, value):
		raise NotImplementedError("Must be overriden")

	def _delete(self):
		self.libxmp_metadata.delete_property(schema_ns=self.namespace.uid, prop_name=self.address)

	# ───────────────────
	# Descriptor protocol

	def __set__(self, owner_object, value):
		raise NotImplementedError("Must be overriden")

	def __delete__(self, obj):
		self._delete()

	# ──────────
	# Properties

	@property
	def is_leaf(self):
		return not self.is_container

	@property
	def is_container(self):
		raise NotImplementedError("Must be overriden")

	@property
	def namespace(self):
		return self._namespace()

	@property
	def libxmp_metadata(self):
		return self.namespace.libxmp_metadata

	@property
	def desynchronized(self):
		return self.libxmp_metadata.does_property_exist(schema_ns = self.namespace.uid,
		                                                prop_name = self.address)

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return "{namespace}@{address}".format(namespace = unicode(self.namespace.uid),
		                                        address = self.address)

class XMPVirtualElement(object, TreeManipulationMixin, FreezeMixin):
	"""
	Element in an XMP packet.

	Abstracts a fully-qualified, absolute address in a namespace of an XMP metadata
	packet. Virtual elements represent an address the corresponding element of which
	may not exist.
	"""

	# ────────────
	# Constructors

	def __init__(self, namespace, address):
		"""
		Constructs a virtual XMP element.

		Arguments:
			namespace: The namespace to which the element belongs to, or None if the
			           element is a namespace itself. No strong reference of it will be
			           kept, only a weakref.
			address: The fully-qualified, absolute address of the element in its namespace.
		"""

		if not isinstance(namespace, weakref.ReferenceType):
			self._namespace = weakref.ref(namespace)
		else:
			self._namespace = namespace
		self.address = address
		self.freeze(XMPVirtualElement)

	# ──────────
	# Properties

	@property
	def namespace(self):
		return self._namespace()

	@property
	def parent(self):
		try:
			return super(XMPVirtualElement, self).parent
		except KeyError:
			return XMPVirtualElement(self.namespace, self.parent_address)

	# ─────────────
	# Attribute API

	def has(self, field_name):
		return False

	def __getattr__(self, name):
		"""
		Creates a child virtual element if normal attribute lookup fails.

		Warning:
		    This may cause confusion if the user wants to actually access a sub-field
		    called namespace or address, which they legitimately may want.
		    Notwithstanding the confusion, the user would have to use __getitem__ in
		    this case.
		"""

		# A subfield of a virtual element is also virtual
		qualified_field_name = self.namespace.qualify(name)
		return XMPVirtualElement(self.namespace, self.absoluteAddress(qualified_field_name))

	def __setattr__(self, name, value):
		if self.frozen and not self.__raw_hasattr__(name):
			child = self.__getattr__(name)
			assert(hasattr(child, "__set__") and callable(child.__set__))
			child.__set__(self, value)
		else:
			object.__setattr__(self, name, value)

	# ───────────
	# [] operator

	def __getitem__(self, key):
		if isinstance(key, (int, long)):
			return XMPVirtualElement(self.namespace, self.absoluteAddress("[%s]"%key))
		elif isinstance(key, basestring):
			qualified_field_name = self.namespace.qualify(key)
			return XMPVirtualElement(self.namespace, self.absoluteAddress(qualified_field_name))
		else:
			raise TypeError("Wrong index type "+str(type(key)))

	# ───────────────────
	# Descriptor protocol

	def __set__(self, owner_object, value):
		"""
		Sets the property in the associated libxmp metadata and adds an XMP element to
		the object tree rooted in the virtual element's namespace.

		Attributes:
			owner_object: object the
		"""

		parent = self.parent
		if type(parent) is XMPVirtualElement:
			# Set was called on chained virtual elements; go up the chain, recursing to the
			# base case where the parent exists.

			# There are only 2 ways to get a child virtual element from a parent virtual
			# element:
			# - with the . attribute operator or [] field-name lookup operator, in which
			#   case the parent (virtual) element will be a struct;
			# - with the [] integer-indexing operator, in which case the parent (virtual)
			#   element is an array.

			if self.is_array_element:
				parent_value = [None] * self.index + [value]
			else:
				parent_value = {self.name : value}

			parent.__set__(owner_object, parent_value)
		else:
			# The parent already exists ; we'll do out part by creating the element, and
			# recursing downwards to let children create themselves if needed.

			new_element = XMPElement.fromValue(self.namespace, self.address, value)
			if self.is_array_element:
				parent.set(self.index, value)
			else:
				parent[self.name] = value

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return "{namespace}@{address} [virtual]".format(namespace = self.namespace.uid,
		                                                  address = self.address)

class XMPStructure(XMPElement, ContainerMixin, collections.Sequence, collections.Mapping):
	""" Convenience wrapper around libXMP to manipulate an XMP struct. """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children):
		XMPElement.__init__(self, namespace, address)
		self.children = children
		self.freeze(XMPStructure)

	# ──────────
	# Properties

	@property
	def children(self):
	    return self._children

	@children.setter
	def children(self, new_children):
		if isinstance(new_children, collections.MutableMapping):
			self._children = new_children
		else:
			self._children = collections.OrderedDict((c.name, c) for c in new_children)

	@property
	def desynchronized(self):
		if not self.libxmp_metadata.does_property_exist(schema_ns = self.namespace.uid,
		                                                prop_name = self.address):
			return True

		# Check that all children exist in the xmp packet
		return any(c.desynchronized for c in self)

		# TODO Check that no element in the xmp packet exist that do not exist among children
		#      (false-negatives)

	# ───────────
	# General API

	def __nonzero__(self):
		return len(self) > 0

	# ───────────────────────────────
	# CRUD API (XMPElement overrides)

	# Warning: This API may desync the object tree. In particular, the create (resp.
	#          delete) function desyncs the object tree; it adds (resp. removes) a
	#          node in the XMP packet without adding (resp. removing) the associated
	#          object in the element's parent.
	#
	#          Take care to add or remove the corresponding object in the parent if
	#          the call was successful.

	def _create(self, value = None):

		if value is None:
			pass
		elif not isinstance(value, collections.Mapping):
			raise TypeError("XMPStructure can only be set with collections.Mapping values; given " + str(type(value)))

		self.libxmp_metadata.set_property(schema_ns = self.namespace.uid,
		                                  prop_name = self.address,
		                                 prop_value = "",
		                       prop_value_is_struct = True)
		if value is not None:
			self.update(value)

	@property
	def value(self):
		return collections.OrderedDict((c.name, c.value) for c in self)

	def update(self, value):
		if value is None:
			self._delete()
		elif not isinstance(value, collections.Mapping):
			raise TypeError("XMPStructure can only be set with collections.Mapping values; given " + str(type(value)))

		for field_name, field_value in value.iteritems():
			self.set(field_name, field_value)

	# ───────────
	# General API

	def attributes(self):
		""" Returns the list of children elements. """
		return list(self._children.iterkeys())

	def fields(self):
		""" Returns the list of children elements; synonymous with attributes(). """
		return self.attributes

	def iterchildren(self):
		""" Returns an iterator over children. """
		return self._children.itervalues()

	def set(self, key, value):
		""" Sets the attribute named key, even if it doesn't exist, and do all book-keeping. """

		qualified_key = self.namespace.qualify(key)
		if self.get(qualified_key, default=None) is None:
			new_element = XMPElement.fromValue(self.namespace,
			                                   self.absoluteAddress(qualified_key),
			                                   value)
			new_element._create(value)
			self._children[qualified_key] = new_element
		elif value is None:
			self._children[qualified_key].delete()
			del self._children[qualified_key]
		else:
			self._children[qualified_key].update(value)

	# ───────────────────
	# Descriptor protocol

	def __set__(self, owner_object, value):
		raise NotImplementedError # TODO

	# ─────────────
	# Attribute API

	def has(self, field_name):
		qualified_field_name = self.namespace.qualify(field_name)
		return any(qualified_field_name == c.name for c in self)

	def __getattr__(self, name):
		"""
		Standard __getattr__ implementing custom field access when __getattribute__'s search fails.

		See:
		    https://docs.python.org/2/reference/datamodel.html#object.__getattr__
		"""

		# self.frozen is safe to call as it will tap into __getattribute__ first, which
		# should find the attribute without coming back here in an infinite recursion
		if not self.frozen:
			raise
		field = self.get(name, default=None)
		if field is not None:
			return field
		else:
			qualified_field_name = self.namespace.qualify(name)
			return XMPVirtualElement(self.namespace, self.absoluteAddress(qualified_field_name))

	def __setattr__(self, name, value):
		"""
		Standard __setattr__ with virtual-element attribute fallback for all non-frozen attributes.

		See:
		    https://docs.python.org/2/reference/datamodel.html#object.__setattr__
		"""

		if self.frozen and not self.__raw_hasattr__(name):
			child = self.__getattr__(name)
			assert(hasattr(child, "__set__") and callable(child.__set__))
			child.__set__(self, value)
		else:
			object.__setattr__(self, name, value)

	def __delattr__(self, name):
		try:
			object.__delattr__(self, name)
		except AttributeError as attribute_error:
			if attribute_error.args[0] != name:
				raise
			child = self.__getattr__(name)
			assert(hasattr(child, "__set__") and callable(child.__set__))
			child.__delete__(self)
			raise

	# ────────────────────────────────────
	# Mutable{Sequence,Mapping} common API

	def __getitem__(self, key_or_index):
		if isinstance(key_or_index, (int,long)):
			return self._children[self.__indexToKey(key_or_index)]
		elif isinstance(key_or_index, slice):
			return [self._children[k] for k in self.__indexToKey(key_or_index)]
		elif not isinstance(key_or_index, basestring):
			raise TypeError("Wrong index type "+str(type(key_or_index)))

		key_components = key_or_index.split("/")
		qualified_field_name = self.namespace.qualify(key_components[0])
		nested_components = key_components[1:]
		try:
			child = self._children[qualified_field_name]
		except KeyError:
			raise KeyError(qualified_field_name)

		if nested_components:
			return child["/".join(nested_components)]
		else:
			return child

	def __setitem__(self, key_or_index, value):
		if isinstance(key_or_index, (int,long)):
			key = self.__indexToKey(key_or_index)
		elif not isinstance(key_or_index, basestring):
			raise TypeError("Wrong index type "+str(type(key_or_index)))
		else:
			key = key_or_index
		self.set(key, value)

	def __delitem__(self, key_or_index):
		if isinstance(key_or_index, (int,long)):
			key = self.__indexToKey(key_or_index)
		elif not isinstance(key_or_index, basestring):
			raise TypeError("Wrong index type "+str(type(key_or_index)))

		element_to_delete = self.__getitem__(key)
		element_to_delete.__delete__()
		return self._children.pop(key)

	def __len__(self):
		return len(self._children)

	def __contains__(self, key):
		if not isinstance(key, basestring):
			raise TypeError("Wrong index type "+str(type(key)))

		key_components = key.split("/")
		qualified_field_name = self.namespace.qualify(key_components[0])
		nested_components = key_components[1:]
		if not nested_components:
			return qualified_field_name in self._children
		else:
			try:
				return "/".join(nested_components) in self[qualified_field_name]
			except KeyError:
				return False

	def __iter__(self):
		return self.iterchildren()

	def pop(self, key = None, **kwargs):
		has_default = "mapping_default" in kwargs
		if key is None and not has_default:
			if len(self) < 1:
				raise IndexError("pop from empty element")
			key = self.keys()[-1]
		elif not isinstance(key, basestring):
			raise TypeError("Wrong index type "+str(type(key_or_index)))

		try:
			return self.__delitem__(key)
		except IndexError:
			if has_default:
				return kwargs["mapping_default"]
			else:
				raise KeyError(key)

	# Note: the following methods are automatically implemented as mixin methods
	#       using the Mapping ABC:
	#       • keys
	#       • items
	#       • values
	#       • get
	#       • popitem
	#       • clear
	#       • update
	#       • setdefault
	# For more information: https://docs.python.org/2/library/collections.html

	# ───────────────────
	# MutableSequence API

	def insert(self, i, value):
		raise NotImplementedError
		# TODO There's seemingly no way to change the order of attributes without
		#      removing and adding them all in the desired order; this could be a lot of
		#      work. If done, this class could be a MutableSequence instead of just a
		#      Sequence.

	# ──────────────
	# Textualization

	def __str__(self):
		children = "\n".join([str(c) for c in self.children])
		return self.name + "\n\t" + children.replace("\n", "\n\t")

	def __unicode__(self):
		if self:
			mid_children_str = [TREE_MID_INDENT+unicode(c) for c in self[:-1]]
			last_child_str = TREE_LAST_INDENT+unicode(self[-1])
			children_str = mid_children_str + [last_child_str]
		else:
			children_str = []
		return self.name + "\n" + "\n".join([c.replace("\n","\n"+INDENT)for c in children_str])

	# ───────
	# Helpers

	def __indexToKey(self, index_or_slice):
		return self._children.keys()[index_or_slice]

class XMPNamespace(XMPStructure):
	""" Convenience wrapper around libXMP to manipulate a namespace. """

	# ──────────
	# Properties

	def __init__(self, xmp, uid):
		XMPStructure.__init__(self, None, "", [])
		if not isinstance(xmp, weakref.ReferenceType):
			self._xmp = weakref.ref(xmp)
		else:
			self._xmp = xmp
		self.uid = uid
		self.freeze(XMPNamespace)

	# ──────────
	# Properties

	@property
	def xmp(self):
		return self._xmp()

	@property
	def namespace(self):
		return self

	@property
	def libxmp_metadata(self):
		return self.xmp.libxmp_metadata

	@property
	def prefix(self):
		return self.libxmp_metadata.get_prefix_for_namespace(self.uid)[:-1]

	@property
	def exists(self):
		return self.uid in self.xmp

	# ───────────────────────────────
	# CRUD API (XMPElement overrides)

	# Warning: This API may desync the object tree. In particular, the create (resp.
	#          delete) function desyncs the object tree; it adds (resp. removes) a
	#          node in the XMP packet without adding (resp. removing) the associated
	#          object in the element's parent.
	#
	#          Take care to add or remove the corresponding object in the parent if
	#          the call was successful.

	def _delete(self):
		for child in self:
			child.delete()

	# ──────────────
	# Comparison API

	def __eq__(self, other):
		return isinstance(other, self.__class__) \
		   and self.xmp is other.xmp \
		   and self.uid == other.uid

	# ───────────
	# Utility API

	def qualify(self, name):
		if isQualified(name): return name
		return qualify(name, self.prefix)

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		if self.children:
			unicode_children = (unicode(e) for e in self.iterchildren())
			return u"{}\n{}".format(self.uid, "\n".join(unicode_children)).replace("\n","\n\t")
		else:
			return self.uid

class XMPArray(XMPElement, ContainerMixin, collections.MutableSequence):
	""" Convenience wrapper around libXMP to manipulate an XMP array (rdf:Seq). """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children):
		XMPElement.__init__(self, namespace, address)
		self._children = children
		self.freeze(XMPArray)

	# ──────────
	# Properties

	@property
	def desynchronized(self):
		if not self.libxmp_metadata.does_property_exist(schema_ns = self.namespace.uid,
		                                                prop_name = self.address):
			return True

		any_child_desynchronized = any(children.desynchronized for c in self.children)
		real_length = self.libxmp_metadata.count_array_items(schema_ns = self.namespace.uid,
		                                                     prop_name = self.address)
		missing_elements = real_length != len(self)

		return any_child_desynchronized or missing_elements

	# ───────────────────────────────
	# CRUD API (XMPElement overrides)

	# Warning: This API may desync the object tree. In particular, the create (resp.
	#          delete) function desyncs the object tree; it adds (resp. removes) a
	#          node in the XMP packet without adding (resp. removing) the associated
	#          object in the element's parent.
	#
	#          Take care to add or remove the corresponding object in the parent if
	#          the call was successful.

	def _create(self, value = None):
		if value is None:
			pass
		elif not isinstance(value, collections.Sequence):
			raise TypeError("XMPArray can only be set with collections.Sequence values; given " + str(type(value)))

		self.libxmp_metadata.set_property(schema_ns = self.namespace.uid,
		                                  prop_name = self.address,
		                                 prop_value = "",
		                        prop_value_is_array = True,
		                      prop_array_is_ordered = True)

		if value is not None:
			self.update(value)

	@property
	def value(self):
		return list(c.value for c in self.children)

	def update(self, value):
		if value is None:
			self._delete()
		elif not isinstance(value, collections.Sequence):
			raise TypeError("XMPArray can only be set with collections.Sequence values; given " + str(type(value)))

		for i, v in enumerate(value):
			self[i] = v

		if len(self) > len(value):
			for i in reversed(range(len(self) - len(value), len(self))):
				del self[i]

	# ────────────────────────
	# ContainerMixin overrides

	@property
	def children(self):
		return self._children

	# ───────────────────
	# Descriptor protocol

	def __set__(self, owner_object, value):
		self.update(value)

	# ───────────
	# General API

	def set(self, i, value):
		"""
		Sets the i-th element to value.

		Contrary to array_element[i] (__getitem__), this will work for indices outside
		of the current array, in which case elements with indices in[len(self)+1, i-1]
		are set to None.
		"""

		if 0 <= i < len(self):
			return self.children[i].__set__(self, value)
		else:
			# Pad with None elements if any needed
			for x in range(len(self), i-1):
				self.append(None)
			# Set the extra element
			self.append(value)

	# ───────────────────
	# MutableSequence API

	def __getitem__(self, i):
		return self._children[i]

	def __setitem__(self, i, value):
		self.set(i, value)

	def __delitem__(self, i):
		element_to_delete = self.children[i]
		element_to_delete.__delete__(self)
		del self._children[i]
		return element_to_delete

	def __len__(self):
		return len(self.children)

	def insert(self, i, value):
		xmp_i = i+1 # libXMP uses 1-indexing
		new_element = XMPElement.fromValue(self.namespace,
		                                   self.absoluteAddress("[%s]"%xmp_i),
		                                   value)
		if isinstance(new_element, XMPValue):
			self.libxmp_metadata.set_array_item(schema_ns  = self.namespace.uid,
			                                    array_name = self.address,
			                                    item_index = xmp_i,
			                                    item_value = None,
			                                    prop_array_insert_before= True)
		new_element._create(value)
		self._children.insert(i, new_element)

	# Note: the following methods are automatically implemented as mixin methods
	#       using the Sequence ABC:
	#       • __reversed__
	#       • index
	#       • count
	#       • append
	#       • reverse
	#       • extend
	#       • remove
	#       • __iadd__
	# For more information: https://docs.python.org/2/library/collections.html

	# ──────────────
	# Textualization

	def __str__(self):
		children_strings = "\n".join(["- "+str(c).replace("\n", "\n  ")
		                              for c in self.children])
		return self.name + " [\n    " + children_strings.replace("\n", "\n    ") + "\n]"

	def __unicode__(self):
		children_strings = "\n".join([u"⁃ "+unicode(c).replace("\n", "\n  ")
		                              for c in self.children])
		return self.name + " [\n    " + children_strings.replace("\n", "\n    ") + "\n]"

class XMPSet(XMPElement, ContainerMixin, collections.MutableSet):
	""" Convenience wrapper around libXMP to manipulate an XMP set (rdf:Bag). """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children):
		super(XMPSet, self).__init__(namespace, address)
		self._children = set(children)
		self.freeze(XMPSet)

	# ──────────
	# Properties

	@property
	def desynchronized(self):
		if not self.libxmp_metadata.does_property_exist(schema_ns = self.namespace.uid,
		                                                prop_name = self.address):
			return True

		any_child_desynchronized = any(children.desynchronized for c in self.children)
		real_length = self.libxmp_metadata.count_array_items(schema_ns = self.namespace.uid,
		                                                     prop_name = self.address)
		missing_elements = real_length != len(self)

		return any_child_desynchronized or missing_elements

	# ───────────────────────────────
	# CRUD API (XMPElement overrides)

	# Warning: This API may desync the object tree. In particular, the create (resp.
	#          delete) function desyncs the object tree; it adds (resp. removes) a
	#          node in the XMP packet without adding (resp. removing) the associated
	#          object in the element's parent.
	#
	#          Take care to add or remove the corresponding object in the parent if
	#          the call was successful.

	def _create(self, value = None):
		if value is None:
			pass
		elif not isinstance(value, collections.Set):
			raise TypeError("XMPSet can only be set with collections.Set values; given " + str(type(value)))

		self.libxmp_metadata.set_property(schema_ns = self.namespace.uid,
		                                  prop_name = self.address,
		                                 prop_value = "",
		                        prop_value_is_array = True,
		                    prop_array_is_unordered = True)

		if value is not None:
			self.update(value)

	@property
	def value(self):
		return set(c.value for c in self.children)

	def update(self, value):
		raise NotImplementedError # TODO

	# ────────────────────────
	# ContainerMixin overrides

	@property
	def children(self):
		return self._children

	# ───────
	# MutableSet API

	def __contains__(self, key):
		return namespace.qualify(key) in [c.name for c in self.children]

	def __iter__(self):
		return iter(self.children)

	def __len__(self):
		return len(self.children)

	def add(self, value):
		raise NotImplementedError # TODO

	def discard(self, key):
		element_to_delete = next(c for c in self.children if c.name == key)
		element_to_delete.__delete__()
		self._children.discard(element_to_delete)

	# ──────────────
	# Textualization

	def __str__(self):
		children_strings = "\n".join(["* "+str(c).replace("\n", "\n  ")
		                              for c in self.children])
		return self.name + " {\n    " + children_strings.replace("\n", "\n    ") + "\n}"

	def __unicode__(self):
		children_strings = "\n".join([u"• "+unicode(c).replace("\n", "\n  ")
		                              for c in self.children])
		return self.name + " {\n    " + children_strings.replace("\n", "\n    ") + "\n}"

class XMPValue(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP value. """

	# ────────────
	# Constructors

	def __init__(self, *args, **kwargs):
		super(XMPValue, self).__init__(*args, **kwargs)
		self.freeze(XMPValue)

	# ──────────
	# Properties

	@property
	def desynchronized(self):
		return not self.libxmp_metadata.does_property_exist(schema_ns = self.namespace.uid,
		                                                    prop_name = self.address)

	# ────────────────────
	# XMPElement overrides

	@property
	def is_container(self):
		return False

	# ───────────────────────────────
	# CRUD API (XMPElement overrides)

	# Warning: This API may desync the object tree. In particular, the create (resp.
	#          delete) function desyncs the object tree; it adds (resp. removes) a
	#          node in the XMP packet without adding (resp. removing) the associated
	#          object in the element's parent.
	#
	#          Take care to add or remove the corresponding object in the parent if
	#          the call was successful.

	def _create(self, value = None):
		self.update(value)

	@property
	def value(self):
		try:
			value = self.libxmp_metadata.get_property(schema_ns = self.namespace.uid,
			                                          prop_name = self.address)
			if value:
				return value
			else:
				return None
		except libxmp.XMPError:
			return None

	def update(self, value):
		if value is None:
			value = ""
		elif not isinstance(value, basestring):
			value = unicode(value)

		self.libxmp_metadata.set_property(schema_ns = self.namespace.uid,
		                                  prop_name = self.address,
		                                 prop_value = value)

	# ───────────────────
	# Descriptor protocol

	def __set__(self, owner_object, value):
		if not isinstance(value, basestring):
			value = unicode(value)

		self.libxmp_metadata.set_property(schema_ns = self.namespace.uid,
		                                  prop_name = self.address,
		                                 prop_value = value)

	# ──────────────
	# Textualization

	def __str__(self):
		value = self.value
		if value is None:
			return self.name + " [virtual]"
		else:
			return self.name + " = " + str(self.value)

	def __unicode__(self):
		return self.name + " = " + unicode(self.value)
