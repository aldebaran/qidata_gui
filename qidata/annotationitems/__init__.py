# -*- coding: utf-8 -*-

"""
This package contains different classes representing structured dataTypes for annotated datasets.
"""

from person import Person
from face import Face
from typedlist import TypedList

def makeAnnotationItems(itemName, data = None):
    if itemName == "Person":
        return Person() if data is None else Person.fromDict(data)
    elif itemName == "Face":
        return Face() if data is None else Face.fromDict(data)
    else:
        raise TypeError("Required annotation item (%s) does not exist"%itemName)

AnnotationTypes = ["Face", "FacialExpression", "Person"]