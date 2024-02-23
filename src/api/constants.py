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


class CloudStorageProvider(Enum):
    """
    Available Cloud Storage provider
    """
    AWS = "AWS_S3"
    AZURE = "AZURE_BLOB_STORAGE"
