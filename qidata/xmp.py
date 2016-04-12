#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Standard Library
import collections
import os.path
import re
import weakref
# XMP
import libxmp
import libxmp.utils

XMP_NS_ALDEBARAN=u"http://aldebaran.com/xmp/0.1"
SUGGESTED_ALDEBARAN_PREFIX=u"aldebaran"
libxmp.exempi.register_namespace(XMP_NS_ALDEBARAN, SUGGESTED_ALDEBARAN_PREFIX)

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
		self.xmp_file = libxmp.XMPFiles(file_path=self.file_path,
		                                open_forupdate=self.rw)
		self.libxmp_metadata = self.xmp_file.get_xmp()

		return self

	def __exit__(self, type, value, traceback):
		if self.rw:
			try:
				self.xmp_file.put_xmp(self.libxmp_metadata)
				self.xmp_file.close_file()
			except:
				raise RuntimeError("Can't serialize XMP to file " + self.file_path)
		elif repr(self._libxmp_metadata) != self.__original_repr:
			message =  "Modified a read-only XMP file; won't be saved"
			raise RuntimeWarning(message)

class XMP(collections.Mapping):
	"""
	Pythonic wrapper around a libxmp XMPMetadata.
	"""

	def __init__(self, libxmp_metadata = libxmp.XMPMeta()):
		self.libxmp_metadata = libxmp_metadata
		self._namespaces = {}
		for ns_uid, elements in self.__dict().iteritems():
			new_namespace = XMPNamespace(self.libxmp_metadata,
			                             ns_uid,
			                             [LibXMPElement(e) for e in elements])
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
		return XMP.textualizeXMPDict(libxmp.utils.object_to_dict(self.libxmp_metadata)).encode("utf-8")

	def xml(self):
		raw_xml = self.libxmp_metadata.serialize_and_format().encode("utf-8")
		return raw_xml

	# ───────
	# Helpers

	def __dict(self):
		return libxmp.utils.object_to_dict(self.libxmp_metadata)

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

class XMPNamespace(collections.MutableMapping, collections.MutableSequence):
	""" Convenience wrapper around libXMP to manipulate a namespace. """

	def __init__(self, libxmp_metadata, namespace_uid, libxmp_elements):
		self.libxmp_metadata = libxmp_metadata
		self.uid = namespace_uid
		self._elements = []
		for e in libxmp_elements:
			if not e.isTopLevel(): continue
			self._elements.append(XMPElement.fromLibXMPTuple(weakref.ref(self), e, libxmp_elements))

	# ──────────
	# Properties

	@property
	def prefix(self):
		return self.libxmp_metadata.get_prefix_for_namespace(self.uid)

	# ─────────────
	# Container API

	def __len__(self):
		return len(self._elements)

	def __iter__(self):
		return iter(self._elements)

	# The following operators make XMPNamespace behave both as a Sequence and a Mapping.
	#
 	# When given an XPath expression, behaves as a mapping of an XML tree.
	# When given a slice or an index, behaves as a sequence of elements.

	def __getitem__(self, key):
		return self._elements[key]

	def __setitem__(self, key, value):
		success = False
		# TODO Create a namespac if necessary
		if success:
			# super(XMP, self).__setitem__(key, value)
			pass

	def __delitem__(self, key):
		success = False
		# TODO Delete the underlying namespace
		if success:
			del self._elements[key]

	def insert(self, key, value):
		success = False
		# TODO Delete the underlying namespace
		if success:
			del self._elements[key]

	# ──────────────
	# Textualization

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return u"{}\n{}".format(self.uid,
		                        "\n".join([unicode(e) for e in self])).replace("\n","\n\t")

class LibXMPElement:
	""" Wrapper around a libXMP iterator element. """

	ARRAY_ELEMENT_REGEX = re.compile(r".*\[\d+\]$")
	INDEX_REGEX = re.compile(r"^\[\d+\]$")

	def __init__(self, tuple):
		self.address    = unicode(tuple[0])
		self.value      = unicode(tuple[1])
		self.descriptor = tuple[2]

	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		rep = self.address
		if self.value: rep += " = " + self.value
		return rep

	# ──────────
	# Predicates

	def isTopLevel(self):
		return "/" not in self.address and not LibXMPElement.ARRAY_ELEMENT_REGEX.match(self.address)

	def isDescendantOf(self, other_element):
		return self.address != other_element.address \
		   and self.address.startswith(other_element.address)

	def isAncestorOf(self, other_element):
		return other_element.isDescendantOf(self)

	def isChildrenOf(self, other_element):
		if not self.address.startswith(other_element.address):
			return False
		address_delta = self.address[len(other_element.address):]
		is_array_element = LibXMPElement.ARRAY_ELEMENT_REGEX.match(address_delta) is not None
		if is_array_element:
			return LibXMPElement.INDEX_REGEX.match(address_delta)
		else:
			return address_delta.count("/") == 1

	def isParentOf(self, other_element):
		return other_element.isChildrenOf(self)

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

class XMPElement:
	""" Convenience wrapper around libXMP to manipulate a generic element. """

	@staticmethod
	def fromLibXMPTuple(namespace, libxmp_element, libxmp_elements):
		descendents = libxmp_element.descendentsIn(libxmp_elements)
		if libxmp_element.descriptor["VALUE_IS_STRUCT"]:
			return XMPStructure(namespace, libxmp_element, descendents)
		elif libxmp_element.descriptor["VALUE_IS_ARRAY"] and libxmp_element.descriptor["ARRAY_IS_ORDERED"]:
			return XMPArray(namespace, libxmp_element, descendents)
		elif libxmp_element.descriptor["VALUE_IS_ARRAY"] and not libxmp_element.descriptor["ARRAY_IS_ORDERED"]:
			return XMPSet(namespace, libxmp_element, descendents)
		else:
			return XMPValue(namespace, libxmp_element)

	def __init__(self, namespace, libxmp_element):
		self._namespace     = namespace
		self.libxmp_element = libxmp_element

	@property
	def address(self):
		return self.libxmp_element.address

	@property
	def namespace(self):
		return self._namespace()

	@property
	def libxmp_metadata(self):
		return self.namespace.libxmp_metadata

class XMPStructure(XMPElement, list):
	""" Convenience wrapper around libXMP to manipulate an XMP struct. """

	def __init__(self, namespace, libxmp_element, descendents = []):
		XMPElement.__init__(self, namespace, libxmp_element)
		for d in libxmp_element.childrenIn(descendents):
			self.append(XMPElement.fromLibXMPTuple(namespace, d, descendents))

	def __str__(self):
		children = "\n".join([str(c) for c in self])
		return self.address + "\n\t" + children.replace("\n", "\n\t")

	def __unicode__(self):
		if self:
			mid_children = [TREE_MID_INDENT+unicode(c) for c in self[:-1]]
			last_child = TREE_LAST_INDENT+unicode(self[-1])
			children = mid_children + [last_child]
		else:
			children = []
		return self.address + "\n" + "\n".join([c.replace("\n","\n"+INDENT)for c in children])

class XMPArray(XMPElement, list):
	""" Convenience wrapper around libXMP to manipulate an XMP array (rdf:Seq). """
	def __init__(self, namespace, libxmp_element, descendents = []):
		XMPElement.__init__(self, namespace, libxmp_element)

		if descendents:
			for d in libxmp_element.childrenIn(descendents):
				self.append(XMPElement.fromLibXMPTuple(namespace, d, descendents))
		else:
			n_elements = self.libxmp_metadata.count_array_items(schema_ns=self.namespace.uid,
			                                                    array_name=self.address)
			for i in range(1,n_elements+1):
				item = self.libxmp_metadata.get_array_item(schema_ns=self.namespace.uid,
				                                           array_prop_name=self.address,
				                                           index=i)
				self.append(XMPValue(self.namespace, "{}[{}]".format(self.address, i)))

	def __str__(self):
		children = "\n".join(["- "+str(c).replace("\n", "\n  ") for c in self])
		return self.address + " [\n\t" + children.replace("\n", "\n\t") + "\n]"

	def __unicode__(self):
		children = "\n".join([u"⁃ "+unicode(c).replace("\n", "\n  ") for c in self])
		return self.address + " [\n\t" + children.replace("\n", "\n\t") + "\n]"

class XMPSet(XMPElement, list):
	""" Convenience wrapper around libXMP to manipulate an XMP set (rdf:Bag). """

	def __init__(self, namespace, libxmp_element, descendents = []):
		XMPElement.__init__(self, namespace, libxmp_element)
		for d in libxmp_element.childrenIn(descendents):
			self.append(XMPElement.fromLibXMPTuple(namespace, d, descendents))

	def __str__(self):
		children = "\n".join(["* "+str(c).replace("\n", "\n  ") for c in self])
		return self.address + " {\n\t" + children.replace("\n", "\n\t") + "\n}"

	def __unicode__(self):
		children = "\n".join([u"• "+unicode(c).replace("\n", "\n  ") for c in self])
		return self.address + " {\n\t" + children.replace("\n", "\n\t") + "\n}"

class XMPValue(XMPElement):
	""" Convenience wrapper around libXMP to manipulate an XMP value. """
	def __init__(self, namespace, address):
		XMPElement.__init__(self, namespace, address)

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
