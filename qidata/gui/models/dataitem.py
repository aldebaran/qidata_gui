# -*- coding: utf-8 -*-

from qidata.xmp import XMPFile, XMPMetadata, ALDEBARAN_NS
from qidata.annotationitems import makeAnnotationItems, AnnotationTypes

class DataItem(object):

    # ───────────
    # Constructor

    def __init__(self, file_path, rw = False):
        self.xmp_file = XMPFile(file_path, rw)
        self.data = None
        self.__annotations = None

    # ──────────
    # Properties

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, new_data):
        self.__data = new_data

    @property
    def annotations(self):
        if self.__annotations is None:
            self.__annotations = dict()
            with self.xmp_file as tmp:
                for annotationClassName in AnnotationTypes:
                    self.__annotations[annotationClassName] = []
                    try:
                        for annotation in self.metadata[annotationClassName]:
                            obj = makeAnnotationItems(annotationClassName, annotation.info.value)
                            loc = annotation.location.value
                            self.__unicodeListToFloatList(loc)
                            self.__annotations[annotationClassName].append([obj, loc])

                    except KeyError, e:
                        # annotationClassName does not exist in file => it's ok
                        pass

        return self.__annotations

    @property
    def rw(self):
        return self.xmp_file.rw

    @property
    def file_path(self):
        return self.xmp_file.file_path

    @property
    def metadata(self):
        return self.xmp_file.metadata[ALDEBARAN_NS]

    @property
    def xmp(self):
        return self.xmp_file.metadata

    # ───────────
    # General API

    def open(self):
        self.xmp_file.__enter__()
        return self

    def close(self):
        self.xmp_file.__exit__(None, None, None)

    def save_annotations(self):
        with self.xmp_file as tmp:
            for (annotationClassName, annotations) in self.__annotations.iteritems():
                self.metadata[annotationClassName] = []
                for annotation in annotations:
                    tmp_dict = dict(info=annotation[0].toDict(), location=annotation[1])
                    tmp_dict["info"]["version"] = annotation[0].version
                    self.metadata.__getattr__(annotationClassName).append(tmp_dict)

    # ───────────
    # Private API

    def __unicodeListToFloatList(self, list_to_convert):
        for i in range(0,len(list_to_convert)):
            if type(list_to_convert[i]) == list:
                self.__unicodeListToFloatList(list_to_convert[i])
            elif type(list_to_convert[i]) in [unicode, str]:
                list_to_convert[i] = float(list_to_convert[i])


    # ───────────────
    # Context Manager

    def __enter__(self):
        return self.open()

    def __exit__(self, type, value, traceback):
        self.xmp_file.__exit__(type, value, traceback)
