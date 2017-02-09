# -*- coding: utf-8 -*-

from image_widget import ImageWidget
from audio_widget import AudioWidget
from dataset_widget import DataSetWidget

# ────────────
# Data Widgets

SUPPORTED_WIDGETS = {
    "IMAGE": ImageWidget,
    "AUDIO": AudioWidget,
    "DATASET": DataSetWidget
}

def makeRawDataWidget(qidata_object):
	"""
    Create relevant widget for required data type.
    :param qidata_object:  Object to display
    :return:  Widget displaying the raw data of the object (``RawDataWidgetInterface``)
    :raise:  TypeError if given type name is unknown
    """
	try:
		return SUPPORTED_WIDGETS[str(qidata_object.type)](qidata_object.raw_data)
	except KeyError:
		msg = "No RawDataWidget available for type %s"%qidata_object.type
		raise TypeError(msg)