""" constants use in the api"""

from enum import Enum


class Indicator(Enum):
    """
    Available Index values
    """

    NDVI = "NDVI"
    EVI = "EVI"
    GNDVI = "GNDVI"
    NDWI = "NDWI"
    CVI = "CVI"
    CVIn = "CVIn"
    LAI = "LAI"


class Question(Enum):
    """
    An enumeration representing a question with possible answers.

    Attributes:
        no (str): The answer "No".
        yes (str): The answer "Yes".
    """

    NO = "No"
    YES = "Yes"
