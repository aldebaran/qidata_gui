# -*- coding: utf-8 -*-

class Face(object):
    """Contains annotation details for a face"""

    def __init__(self, name="", age=0, fid=0, facial=[]):
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
            return Face(face_data["name"],
                int(face_data["age"]),
                int(face_data["id"])
                )

    @property
    def version(self):
        return 0.1

