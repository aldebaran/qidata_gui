#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import collections
import os.path
import re
import weakref
# XMP
import libxmp

ALDEBARAN_NS_1=u"http://aldebaran.com/xmp/1"
SUGGESTED_ALDEBARAN_NS_PREFIX=u"aldebaran"
libxmp.exempi.register_namespace(ALDEBARAN_NS_1, SUGGESTED_ALDEBARAN_NS_PREFIX)

# ─────────────────────
# Formatting parameters

INDENT_SIZE = 5
INDENT = ' ' * INDENT_SIZE
TREE_INDENT = u'─'*(INDENT_SIZE-2) + " "
TREE_MID_INDENT  = u"├" + TREE_INDENT
TREE_LAST_INDENT = u"└" + TREE_INDENT

class XMPFile(object):
	def __init__(self, file_path, rw = False):
		self.rw               = rw
		self.file_path        = os.path.abspath(file_path)
		self.xmp_file         = None
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

	# ──────────
	# Public API

	def __str__(self):
		return "XMP file {}:\n{}".format(self.file_path, str(self.metadata))

	# ───────────────
	# Context Manager

	def __enter__(self):
		if libxmp.exempi.files_check_file_format(self.file_path) == libxmp.consts.XMP_FT_UNKNOWN:
			raise RuntimeError("Unknown XMP file type")
		self.xmp_file = libxmp.XMPFiles(file_path=self.file_path,
		                                open_onlyxmp=True,
		                                open_forupdate=self.rw)
		self.libxmp_metadata = self.xmp_file.get_xmp()

		return self

	def __exit__(self, type, value, traceback):
		try:
			if self.rw:
				try:
					if self.xmp_file.can_put_xmp(self.libxmp_metadata):
						self.xmp_file.put_xmp(self.libxmp_metadata)
					else:
						raise
				except:
					raise RuntimeError("Can't serialize XMP to file " + self.file_path)
			elif repr(self._libxmp_metadata) != self.__original_repr:
				message =  "Modified a read-only XMP file; won't be saved"
				raise RuntimeWarning(message)
		finally:
			self.xmp_file.close_file()


class XMPMetadata(collections.Mapping):
	"""
	Pythonic wrapper around a libxmp XMPMetadata.
	"""

	def __init__(self, libxmp_metadata = libxmp.XMPMeta()):
		self.libxmp_metadata = libxmp_metadata
		self._namespaces = {}

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
			namespace_weakref = weakref.ref(namespace)
			libxmp_members = namespace.childrenIn(ns_libxmp_descendents)
			members = [XMPElement.fromLibXMP(m, ns_libxmp_descendents, namespace_weakref) for m in libxmp_members]
			namespace.children = members
			self._namespaces[ns_uid] = namespace

	# ──────────
	# Properties

	@property
	def namespaces(self):
		return [n for n in self._namespaces.itervalues()]

	# ───────────
	# Mapping API

	def __len__(self):
		return len(self._namespaces)

	def __iter__(self):
		return iter(self._namespaces)

	def __getitem__(self, key):
		return self._namespaces[key]

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return "\n".join([unicode(n) for n in self.namespaces])

	def pretty_str(self):
		import libxmp.utils
		return XMP.textualizeXMPDict(libxmp.utils.object_to_dict(self.libxmp_metadata)).encode("utf-8")

	def xml(self):
		raw_xml = self.libxmp_metadata.serialize_and_format().encode("utf-8")
		return raw_xml

	# ───────
	# Helpers

	@staticmethod
	def textualizeXMPDict(x, indent = ""):
		rep = ""
		if isinstance(x, dict):
			rep += ("\n"+indent).join([str(k)+": " + XMP.textualizeXMPDict(v, indent+' '*(2+len(str(k)))) for k,v in x.iteritems()])
		elif isinstance(x, list):
			rep += ("\n"+indent).join([u"⁃ " + XMP.textualizeXMPDict(e, indent+' '*2) for e in x])
		elif isinstance(x, tuple) and len(x) == 3:
			node_name  = x[0]
			node_value = x[1]
			rep += node_name + " = " + node_value
		else:
			return str(x)
		return rep

class XMPTreeOperationMixin:
	"""
	Defines tree operations for any element that has a namespace and address.
	"""

	# ──────────
	# Properties

	@property
	def namespace_uid(self):
		if isinstance(self, LibXMPElement):
			return self.namespace
		elif isinstance(self, XMPElement):
			return self.namespace.uid

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
		is_array_element = LibXMPElement.ARRAY_ELEMENT_REGEX.match(address_delta) is not None
		other_is_namespace = not other.address

		if other_is_namespace and not is_array_element:
			# If other is a namespace, its address is the empty string and
			# children don't have a / in their address
			return address_delta.count("/") == 0
		elif is_array_element:
			return bool(LibXMPElement.INDEX_REGEX.match(address_delta))
		else:
			return address_delta.count("/") == 1

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

class LibXMPElement(object, XMPTreeOperationMixin):
	""" Wrapper around a libXMP iterator element. """

	ARRAY_ELEMENT_REGEX = re.compile(r".*\[\d+\]$")
	INDEX_REGEX = re.compile(r"^\[\d+\]$")

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

	@property
	def is_top_level(self):
		return "/" not in self.address and not LibXMPElement.ARRAY_ELEMENT_REGEX.match(self.address)

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

class XMPElement(object, XMPTreeOperationMixin):
	""" Convenience wrapper around libXMP to manipulate a generic element. """

	# ────────────
	# Constructors

	def __init__(self, namespace, address):
		assert(namespace is None or isinstance(namespace, weakref.ReferenceType))
		self._namespace = namespace
		self.address    = address

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
			                                           namespace) for libxmp_child in libxmp_children]

			# Return the assembled tree
			if libxmp_element.is_struct:
				return XMPStructure(namespace, libxmp_element.address, children_elements)
			elif libxmp_element.is_array:
				return XMPArray(namespace, libxmp_element.address, children_elements)
			elif libxmp_element.is_set:
				return XMPSet(namespace, libxmp_element.address, children_elements)

	# ──────────
	# Properties

	@property
	def is_leaf(self):
		try:
			return not self.is_container
		except NotImplemented:
			return NotImplemented(str(self))

	@property
	def is_container(self):
		return NotImplemented(str(self))

	@property
	def namespace(self):
		return self._namespace()

	@property
	def name(self):
		return self.address.split("/")[-1]

	@property
	def libxmp_metadata(self):
		return self.namespace.libxmp_metadata

class XMPStructure(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP struct. """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children):
		XMPElement.__init__(self, namespace, address)
		self.children = children

	# ────────────────────
	# XMPElement overrides

	@property
	def is_container(self):
		return True

	# ──────────
	# Properties

	@property
	def children(self):
		return [c for c in self._children.itervalues()]

	@children.setter
	def children(self, new_children):
		if isinstance(new_children, collections.MutableMapping):
			self._children = new_children
		else:
			self._children = dict((c.name, c) for c in new_children)

	# ─────────────
	# Attribute API

	def has(self, field_name):
		return field_name in self._children

	def __getattr__(self, name):
		print name
		# TODO

	# ──────────────
	# Textualization

	def __str__(self):
		children = "\n".join([str(c) for c in self.children])
		return self.name + "\n\t" + children.replace("\n", "\n\t")

	def __unicode__(self):
		if self.children:
			mid_children = [TREE_MID_INDENT+unicode(c) for c in self.children[:-1]]
			last_child = TREE_LAST_INDENT+unicode(self.children[-1])
			children = mid_children + [last_child]
		else:
			children = []
		return self.name + "\n" + "\n".join([c.replace("\n","\n"+INDENT)for c in children])

class XMPArray(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP array (rdf:Seq). """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children):
		XMPElement.__init__(self, namespace, address)
		self.children = children

	# ────────────────────
	# XMPElement overrides

	@property
	def is_container(self):
		return True

	# ──────────────
	# Textualization

	def __str__(self):
		children_strings = "\n".join(["- "+str(c).replace("\n", "\n  ") for c in self.children])
		return self.name + " [\n    " + children_strings.replace("\n", "\n    ") + "\n]"

	def __unicode__(self):
		children_strings = "\n".join([u"⁃ "+unicode(c).replace("\n", "\n  ") for c in self.children])
		return self.name + " [\n    " + children_strings.replace("\n", "\n    ") + "\n]"

class XMPSet(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP set (rdf:Bag). """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children):
		XMPElement.__init__(self, namespace, address)
		self.children = set(children)

	# ────────────────────
	# XMPElement overrides

	@property
	def is_container(self):
		return True

	# ──────────────
	# Textualization

	def __str__(self):
		children_strings = "\n".join(["* "+str(c).replace("\n", "\n  ") for c in self.children])
		return self.name + " {\n    " + children_strings.replace("\n", "\n    ") + "\n}"

	def __unicode__(self):
		children_strings = "\n".join([u"• "+unicode(c).replace("\n", "\n  ") for c in self.children])
		return self.name + " {\n    " + children_strings.replace("\n", "\n    ") + "\n}"

class XMPValue(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP value. """

	@property
	def value(self):
		return self.libxmp_metadata.get_property(schema_ns=self.namespace.uid, prop_name=self.address)

	# ────────────────────
	# XMPElement overrides

	@property
	def is_container(self):
		return False

	# ──────────────
	# Textualization

	def __str__(self):
		return self.name + " = " + str(self.value)

	def __unicode__(self):
		return self.name + " = " + unicode(self.value)

class XMPNamespace(XMPStructure):
	""" Convenience wrapper around libXMP to manipulate a namespace. """

	# ──────────
	# Properties

	def __init__(self, xmp, uid):
		XMPStructure.__init__(self, None, "", [])
		self.xmp = xmp
		self.uid = uid

	# ──────────
	# Properties

	@property
	def namespace(self):
		return self

	@property
	def libxmp_metadata(self):
		return self.xmp.libxmp_metadata

	@property
	def prefix(self):
		return self.libxmp_metadata.get_prefix_for_namespace(self.uid)

	# ──────────────
	# Comparison API

	def __eq__(self, other):
		return isinstance(other, self.__class__) \
		   and self.xmp is other.xmp \
		   and self.uid == other.uid

	# ────────────
	# Sequence API

	def __len__(self):
		return len(self.children)

	def __iter__(self):
		return iter(self.children)

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		if self.children:
			return u"{}\n{}".format(self.uid,
			                        "\n".join([unicode(e) for e in self.children])).replace("\n","\n\t")
		else:
			return self.uid
