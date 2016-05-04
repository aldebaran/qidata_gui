# -*- coding: utf-8 -*-

from typedlist import TypedList

class FacialExpression(object):
    """Contains annotation details for a face"""

    def __init__(self):
        super(FacialExpression, self).__init__()
        self.valence = 0
        self.smile_level = 0.5
        self.tamereenshort = [0,0]

class Face(object):
    """Contains annotation details for a face"""

    def __init__(self, name="", age=0, fid=0):
        super(Face, self).__init__()
        self.name = name
        self.age = age
        self.id = fid

    def toDict(self):
        return dict(name=self.name,
            age=self.age,
            id=self.id,
            )

    @staticmethod
    def fromDict(face_data):
        # Here we could discriminate how the dict is read, depending
        # on the message's version used.
        if not face_data.has_key("version") or float(face_data["version"]) > 0:
            # name : str
            # age : int
            # id : int
            return Face(face_data["aldebaran:name"] if face_data.has_key("aldebaran:name") else "",
                int(face_data["aldebaran:age"]) if face_data.has_key("aldebaran:age") else 0,
                int(face_data["aldebaran:id"]) if face_data.has_key("aldebaran:id") else 0
                )

    @property
    def version(self):
        return 0.1

