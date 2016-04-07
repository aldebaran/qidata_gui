#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import libxmp
import libxmp.utils

XMP_NS_ALDEBARAN=u"http://aldebaran.com/xmp/0.1"
SUGGESTED_ALDEBARAN_PREFIX=u"aldebaran"
libxmp.exempi.register_namespace(XMP_NS_ALDEBARAN, SUGGESTED_ALDEBARAN_PREFIX)

class XMP:
    def __init__(self, file_path, rw = False):
        self.rw           = rw
        self.file_path    = file_path
        self.xmp_file     = None
        self.xmp_metadata = None

    # ──────────
    # Public API

    def __str__(self):
        return self.textualize()

    def xml(self):
        return self.xmp_metadata.serialize_and_format(omit_packet_wrapper=True).encode('ascii', 'ignore')

    # ───────
    # Helpers

    def textualize(self):
        return XMP.textualizeXMPDict(libxmp.utils.file_to_dict(self.file_path))

    @staticmethod
    def textualizeXMPDict(x, indent = ""):
        rep = ""
        if isinstance(x, dict):
            rep += ("\n"+indent).join([str(k)+": " + XMP.textualizeXMPDict(v, indent+' '*(2+len(str(k)))) for k,v in x.iteritems()])
        elif isinstance(x, list):
            rep += ("\n"+indent).join(["⁃ " + XMP.textualizeXMPDict(e, indent+' '*2) for e in x])
        elif isinstance(x, tuple) and len(x) == 3:
            rep += str(x[0]) + " = " + str(x[1])
        else:
            return str(x)
        return rep

    # ───────────────
    # Context Manager

    def __enter__(self):
        self.xmp_file     = libxmp.XMPFiles(file_path=self.file_path, open_forupdate=self.rw)
        self.xmp_metadata = self.xmp_file.get_xmp()

        return self

    def __exit__(self, type, value, traceback):
        if self.rw:
            self.xmp_file.put_xmp(self.xmp_metadata)
            self.xmp_file.close_file()

# def saveXMPFace(file_path, bounding_box):
#     xmp_file = libxmp.XMPFiles(file_path=f, open_forupdate=True)
#     xmp_metadata = xmp_file.get_xmp()
#     prefix = xmp_metadata.get_prefix_for_namespace(XMP_NS_ALDEBARAN)

#     # DELETE
#     xmp_metadata.delete_property(schema_ns=XMP_NS_ALDEBARAN,
#                                  prop_name=prefix+"Person")

#     # CREATE an array if it doesn't exist

#     # SET
#     xmp_metadata.set_property(schema_ns=XMP_NS_ALDEBARAN,
#                               prop_name=prefix+"Person/"+prefix+"Face/"+prefix+"BoundingBox/"+prefix+"TopLeft",
#                               prop_value="0,0")
#     xmp_metadata.set_property(schema_ns=XMP_NS_ALDEBARAN,
#                               prop_name=prefix+"Person/"+prefix+"Face/"+prefix+"BoundingBox/"+prefix+"TopRight",
#                               prop_value="230,120")
#     xmp_metadata.append_array_item(schema_ns=XMP_NS_ALDEBARAN,
#                                    array_name=prefix+"Person/"+prefix+"Face/"+prefix+"BoundingBox/"+prefix+"ListBB",
#                                    item_value=None,
#                                    array_options={"prop_value_is_array":True, "prop_array_is_ordered":True})
#     xmp_metadata.append_array_item(schema_ns=XMP_NS_ALDEBARAN,
#                                    array_name=prefix+"Person/"+prefix+"Face/"+prefix+"BoundingBox/"+prefix+"ListBB",
#                                    item_value="None")
#     xmp_metadata.set_array_item(schema_ns=XMP_NS_ALDEBARAN,
#                                 array_name=prefix+"Person/"+prefix+"Face/"+prefix+"BoundingBox/"+prefix+"ListBB",
#                                 item_index=1,
#                                 item_value="0")

#     if xmp_file.can_put_xmp(xmp_metadata):
#         xmp_file.put_xmp(xmp_metadata)
#         xmp_file.close_file()
