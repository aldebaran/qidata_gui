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
		self.metadata = XMP(self._libxmp_metadata)

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

class XMPTreeOperations:
	# ──────────
	# Predicates

	def inSameNamespace(self, other):
		return self.namespace == other.namespace

	def isDescendantOf(self, other):
		return self.address.startswith(other.address) \
		   and self.inSameNamespace(other) \
		   and self.address != other.address

	def isAncestorOf(self, other):
		return other.isDescendantOf(self)

	def isChildrenOf(self, other):
		print type(self), type(other)
		if not self.address.startswith(other.address) or \
		   not self.inSameNamespace(other):
			return False

		address_delta = self.address[len(other.address):]
		is_array_element = LibXMPElement.ARRAY_ELEMENT_REGEX.match(address_delta) is not None
		if is_array_element:
			return LibXMPElement.INDEX_REGEX.match(address_delta)
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
		# for e in elements:
		# 	print self.address, e.address, e.isChildrenOf(self)
		return [e for e in elements if e.isChildrenOf(self)]

	def parentsIn(self, elements):
		return [e for e in elements if e.isParentOf(self)]

class LibXMPElement(XMPTreeOperations):
	""" Wrapper around a libXMP iterator element. """

	ARRAY_ELEMENT_REGEX = re.compile(r".*\[\d+\]$")
	INDEX_REGEX = re.compile(r"^\[\d+\]$")

	def __init__(self, tuple):
		self.namespace  = unicode(tuple[0])
		self.address    = unicode(tuple[1])
		self.value      = unicode(tuple[2])
		self.descriptor = tuple[3]

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		rep = self.address
		if self.value: rep += " = " + self.value
		return rep

	# ──────────
	# Properties

	@property
	def is_namespace(self):
	    return self.descriptor["IS_SCHEMA"]

	@property
	def is_top_level(self):
		return "/" not in self.address and not LibXMPElement.ARRAY_ELEMENT_REGEX.match(self.address)

class XMP(collections.Mapping):
	"""
	Pythonic wrapper around a libxmp XMPMetadata.
	"""

	def __init__(self, libxmp_metadata = libxmp.XMPMeta()):
		self.libxmp_metadata = libxmp_metadata
		self._namespaces = {}

		# Group all elements by namespace and parse them in LibXMPElements
		element_dictionary = {}
		for libxmp_tuple in self.libxmp_metadata:
			if libxmp_tuple[-1]["IS_SCHEMA"]: continue
			ns_uid = libxmp_tuple[0]
			libxmp_element = LibXMPElement(libxmp_tuple)
			try:
				element_dictionary[ns_uid].append(libxmp_element)
			except KeyError:
				element_dictionary[ns_uid] = [libxmp_element]

		# Build namespace elements
		for ns_uid, libxmp_elements in element_dictionary.iteritems():
			new_namespace = XMPNamespace(libxmp_metadata, ns_uid, libxmp_elements)
			self._namespaces[ns_uid] = new_namespace

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

class XMPElement(XMPTreeOperations):
	""" Convenience wrapper around libXMP to manipulate a generic element. """

	# ────────────
	# Constructors

	def __init__(self, namespace, address, children = None):
		self._namespace = namespace
		self._address   = address
		self.children   = children

	def addChildrenFrom(self, libxmp_elements):
		# print "Adding elements in", self.address, "among", [e.address for e in libxmp_elements]
		for child in self.childrenIn(libxmp_elements):
			self.children.append(XMPElement.fromLibXMPTuple(self.namespace, child, libxmp_elements))

	@staticmethod
	def fromLibXMPTuple(namespace, element, elements):
		descendents = element.descendentsIn(elements)
		if element.descriptor["VALUE_IS_STRUCT"]:
			return XMPStructure(namespace, element, descendents)
		elif element.descriptor["VALUE_IS_ARRAY"] and element.descriptor["ARRAY_IS_ORDERED"]:
			return XMPArray(namespace, element, descendents)
		elif element.descriptor["VALUE_IS_ARRAY"] and not element.descriptor["ARRAY_IS_ORDERED"]:
			return XMPSet(namespace, element, descendents)
		else:
			return XMPValue(namespace, element)

	# ──────────
	# Properties

	@property
	def namespace(self):
		return self._namespace()

	@property
	def address(self):
		return self._address

	@property
	def libxmp_metadata(self):
		return self.namespace.libxmp_metadata

class XMPNamespace(XMPElement):
	""" Convenience wrapper around libXMP to manipulate a namespace. """

	def __init__(self, libxmp_metadata, namespace_uid, elements):
		XMPElement.__init__(self, None, None, [])
		self._libxmp_metadata = libxmp_metadata
		self.uid = namespace_uid

		for e in elements:
			if not e.is_top_level: continue
			self.children.append(XMPElement.fromLibXMPTuple(weakref.ref(self), e, elements))

	# ──────────
	# Properties

	@property
	def namespace(self):
		return self

	@property
	def prefix(self):
		return self.libxmp_metadata.get_prefix_for_namespace(self.uid)

	@property
	def libxmp_metadata(self):
		return self._libxmp_metadata

	# ──────────────
	# Comparison API

	def __eq__(self, other):
		return isinstance(other, self.__class__) \
		   and self._libxmp_metadata is other._libxmp_metadata \
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
		return u"{}\n{}".format(self.uid,
		                        "\n".join([unicode(e) for e in self])).replace("\n","\n\t")

class XMPStructure(XMPElement, list):
	""" Convenience wrapper around libXMP to manipulate an XMP struct. """

	def __init__(self, namespace, element, descendents = []):
		XMPElement.__init__(self, namespace, element.address, [])
		self.addChildrenFrom(descendents)

	def __str__(self):
		children = "\n".join([str(c) for c in self.children])
		return self.address + "\n\t" + children.replace("\n", "\n\t")

	def __unicode__(self):
		if self.children:
			mid_children = [TREE_MID_INDENT+unicode(c) for c in self.children[:-1]]
			last_child = TREE_LAST_INDENT+unicode(self.children[-1])
			children = mid_children + [last_child]
		else:
			children = []
		return self.address + "\n" + "\n".join([c.replace("\n","\n"+INDENT)for c in children])

class XMPArray(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP array (rdf:Seq). """
	def __init__(self, namespace, libxmp_element, descendents = []):
		XMPElement.__init__(self, namespace, libxmp_element.address, [])
		self.addChildrenFrom(descendents)

		# if descendents:
		# 	n_elements = self.libxmp_metadata.count_array_items(schema_ns=self.namespace.uid,
		# 	                                                    array_name=self.address)
		# 	for i in range(1,n_elements+1):
		# 		item = self.libxmp_metadata.get_array_item(schema_ns=self.namespace.uid,
		# 		                                           array_prop_name=self.address,
		# 		                                           index=i)
		# 		self.append(XMPValue(self.namespace, "{}[{}]".format(self.address, i)))

	def __str__(self):
		children_strings = "\n".join(["- "+str(c).replace("\n", "\n  ") for c in self.children])
		return self.address + " [\n\t" + children_strings.replace("\n", "\n\t") + "\n]"

	def __unicode__(self):
		children_strings = "\n".join([u"⁃ "+unicode(c).replace("\n", "\n  ") for c in self.children])
		return self.address + " [\n\t" + children_strings.replace("\n", "\n\t") + "\n]"

class XMPSet(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP set (rdf:Bag). """

	def __init__(self, namespace, libxmp_element, descendents = []):
		XMPElement.__init__(self, namespace, libxmp_element.address, descendents)
		self.addChildrenFrom(descendents)

	def __str__(self):
		children_strings = "\n".join(["* "+str(c).replace("\n", "\n  ") for c in self.children])
		return self.address + " {\n\t" + children_strings.replace("\n", "\n\t") + "\n}"

	def __unicode__(self):
		children_strings = "\n".join([u"• "+unicode(c).replace("\n", "\n  ") for c in self.children])
		return self.address + " {\n\t" + children_strings.replace("\n", "\n\t") + "\n}"

class XMPValue(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP value. """
	def __init__(self, namespace, libxmp_element):
		XMPElement.__init__(self, namespace, libxmp_element.address)

	@property
	def value(self):
		return self.libxmp_metadata.get_property(schema_ns=self.namespace.uid,
		                                         prop_name=self.address)

	@property
	def name(self):
		return self.address

	def __str__(self):
		return self.name + " = " + str(self.value)

	def __unicode__(self):
		return self.name + " = " + unicode(self.value)
