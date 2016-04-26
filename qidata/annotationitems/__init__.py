# -*- coding: utf-8 -*-

from person import Person
from face import Face

__all__ = ["Face", "Person"]

def makeAnnotationItems(itemName):
    if itemName == "Person":
        return Person()
    elif itemName == "Face":
        return Face()
    else:
        raise TypeError("Required annotation item (%s) does not exist"%itemName)
