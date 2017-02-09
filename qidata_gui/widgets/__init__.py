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

from qidata_widget import QiDataWidget
from qidataset_widget import QiDataSetWidget

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
