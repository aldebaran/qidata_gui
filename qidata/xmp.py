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

class XMP(dict):
	"""
	Pythonic wrapper around a libxmp XMPMetadata.
	"""

	def __init__(self, libxmp_metadata):
		self.libxmp_metadata = libxmp_metadata
		for namespace, elements in self.__dict().iteritems():
			self[namespace] = XMPNamespace(self.libxmp_metadata,
			                               namespace,
			                               [LibXMPElement(e) for e in elements])

	# ──────────
	# Properties

	@property
	def namespaces(self):
	    return self.itervalues()

	# ──────────
	# Public API

	def __str__(self):
		return self.textualize()

	def prettyPrint(self):
		return XMP.textualizeXMPDict(libxmp.utils.object_to_dict(self.libxmp_metadata)).encode("utf-8")

	def xml(self):
		raw_xml = self.libxmp_metadata.serialize_and_format().encode("utf-8")
		return raw_xml

	# ───────
	# Helpers

	def __dict(self):
		return libxmp.utils.object_to_dict(self.libxmp_metadata)

	def textualize(self):
		return "\n".join([str(n) for n in self.namespaces])

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

class XMPNamespace(list):
	def __init__(self, libxmp_metadata, namespace_uid, libxmp_elements):
		self.libxmp_metadata = libxmp_metadata
		self.uid = namespace_uid
		for e in libxmp_elements:
			if not e.isTopLevel(): continue
			self.append(XMPElement.fromLibXMPTuple(weakref.ref(self), e, libxmp_elements))

	@property
	def prefix(self):
	    return self.libxmp_metadata.get_prefix_for_namespace(self.uid)

	def __str__(self):
		return "{}\n{}".format(self.uid,
		                       "\n".join([str(e) for e in self])).replace("\n","\n\t")

class LibXMPElement:
	INDEX_REGEX = re.compile(r".*\[\d+\]$")

	def __init__(self, tuple):
		self.address    = tuple[0]
		self.value      = tuple[1]
		self.descriptor = tuple[2]

	def __str__(self):
		rep = self.address
		if self.value: rep += " = " + self.value
		return rep

	# ──────────
	# Predicates

	def isTopLevel(self):
		return "/" not in self.address and not LibXMPElement.INDEX_REGEX.match(self.address)

	def isDescendantOf(self, other_element):
		return self.address != other_element.address \
		   and self.address.startswith(other_element.address)

	def isAncestorOf(self, other_element):
		return other_element.isDescendantOf(self)

	def isChildrenOf(self, other_element):
		if not self.address.startswith(other_element.address):
			return False
		address_delta = self.address[len(other_element.address):]
		levels_down = address_delta.count("/")
		is_array_element = LibXMPElement.INDEX_REGEX.match(address_delta) is not None
		array_children = levels_down == 0 and is_array_element
		struct_children = levels_down == 1 and not is_array_element
		return array_children or struct_children

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
	def __init__(self, namespace, libxmp_element, descendents = []):
		XMPElement.__init__(self, namespace, libxmp_element)
		for d in libxmp_element.childrenIn(descendents):
			self.append(XMPElement.fromLibXMPTuple(namespace, d, descendents))

	def __str__(self):
		children = "\n".join([str(c) for c in self])
		return self.address + "\n\t" + children.replace("\n", "\n\t")

class XMPArray(XMPElement, list):
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
		children = "\n".join([str(c) for c in self])
		return self.address + "\n\t" + children.replace("\n", "\n\t")

class XMPSet(XMPElement, list):
	def __init__(self, namespace, address, descendents = []):
		XMPElement.__init__(self, namespace, address)
		for d in libxmp_element.childrenIn(descendents):
			self.append(XMPElement.fromLibXMPTuple(namespace, d, descendents))

	def __str__(self):
		children = "\n".join([str(c) for c in self])
		return self.address + "\n\t" + children.replace("\n", "\n\t")

class XMPValue(XMPElement):
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
