# -*- coding: utf-8 -*-

# Qt
from PySide.QtGui import QPixmap
# qidata
from ..dataitem import DataItem
from qidata.xmp import XMPVirtualElement
from qidata.annotationitems import *

class Image(DataItem):

    # ───────────
    # Constructor

    def __init__(self, source_path):
        # Load XMP and open it
        super(Image, self).__init__(source_path, True)

        # Load image
        self.data = QPixmap()
        self.data.load(source_path)

        self.annotations = dict()
        self.load_annotations()

    def load_annotations(self):
        with self.xmp_file as tmp:
            if not isinstance(self.metadata.persons, XMPVirtualElement):
                self.annotations["persons"] = []
                for person in self.metadata.persons:
                    self.annotations["persons"].append([Person.fromDict(person.info), person.location])

            if not isinstance(self.metadata.faces, XMPVirtualElement):
                self.annotations["faces"] = []
                for face in self.metadata.faces:
                    self.annotations["faces"].append([Face.fromDict(face.info), face.location])

    def save_annotations(self):
        with self.xmp_file as tmp:
            self.metadata.persons = []
            self.metadata.faces = []

            for annotations in self.annotations.values():
                for annotation in annotations:
                    tmp_dict = dict(info=annotation[0].toDict(), location=annotation[1])
                    tmp_dict["info"]["version"] = annotation[0].version

                    if isinstance(annotation[0], Person):
                        self.metadata.persons.append(tmp_dict)

                    elif isinstance(annotation[0], Face):
                        # print tmp_dict
                        self.metadata.faces.append(tmp_dict)
