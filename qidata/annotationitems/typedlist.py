# -*- coding: utf-8 -*-

class TypedList(list):

    # ───────────
    # Constructor

    def __init__(self, typename, args=[]):
        self.__typename = typename
        for element in args:
            if(not isinstance(element, self.__typename)):
                msg = "TypedList: list elements are expected to be %s. %s received"
                msg = msg%(self.__typename, type(element))
                raise TypeError(msg)
        super(TypedList, self).__init__(args)


    # ───────
    # Methods

    def append(self, element=None):
        if element is None:
            return
        if isinstance(element, self.__typename):
            super(TypedList, self).append(element)
        else:
            msg = "TypedList: list elements are expected to be %s. %s received"
            msg = msg%(self.__typename, type(element))
            raise TypeError(msg)

    def appendDefault(self):
        self.append(self.__typename())

    # ──────────
    # Properties

    @property
    def typename(self):
        return self.__typename