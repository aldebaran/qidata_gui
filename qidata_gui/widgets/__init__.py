# -*- coding: utf-8 -*-

"""
    ``qidata_gui.widgets`` module
    =============================

    This module is based on Qt and provides convenient widgets to display and
    edit metadata objects provided by the qidata library.

    Widgets and items
    -----------------

    In this package are provided what we called "widgets" and "items".

    * "Widgets" corresponds to an extension of Qt's QWidget class
    * "Items" are extension of different elements included in a specific QWidget
    and are meant to represent a metadata object.

    For instance, an image will be displayed using `data_widgets.ImageWidget`,
    which extends QGraphicsView (which extends itself QWidget).
    On that image, a Face object will be displayed using a `MetadataRectItem`
    which extends QGraphicsRectItem

    A widget is provided for each specific type of data that can be used, and an
    item is provided for each possible representation of a metadata object on
    raw data.
"""

# Standard Library
import re

from main_widget import MainWidget


def makeWidget(widget_type, main_data=None):
    """
    Create relevant widget for required data type.
    :param widget_type:  Name of the data type to display with the widget (str)
    :param main_data:  Data to display
    :return:  Widget containing the given data (MainWidget)
    :raise:  TypeError if given type name is unknown
    """
    for qidata_file_type in LOOKUP_WIDGET_MODEL:
        if widget_type == qidata_file_type:
            return MainWidget(LOOKUP_WIDGET_MODEL[qidata_file_type](main_data))
    raise TypeError("No available widget for %s, available types are %s"
                        %(widget_type, LOOKUP_WIDGET_MODEL.keys())
                    )

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
