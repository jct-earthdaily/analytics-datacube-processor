"""utils class"""

import json
from datetime import datetime
import tempfile
import os
import xarray
from shapely import wkt
from shapely.geometry import shape
from byoa.telemetry.log_manager import log_manager


def dataset_to_zarr_format(dataset: xarray.Dataset):
    """
        Save a xarray.Dataset as zarr format in a temporary folder.
        Output zarr path : "Year-Month-Day_Hour-Minute-Second_analytics-datacube.zarr"

        Args:
            - dataset: the Dataset to save

        Returns:
            The complete zarr path
    """
    logger = log_manager.LogManager.get_instance()

    # Make a valid path whatever the OS
    zarr_path = os.path.join(tempfile.gettempdir(),
                             datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_analytics-datacube.zarr")
    logger.info("AnalyticsDatacube:save_dataset_to_temporary_zarr: path is " + zarr_path)

    # save dataset and return complete zarr path
    dataset.to_zarr(zarr_path)
    return zarr_path


def is_valid_wkt(geometry):
    """ check if the geometry is a valid WKT
    Args:
        geometry : A string representing the geometry

    Returns:
        boolean (True/False)

    """
    try:
        wkt.loads(geometry)
        return True
    except ValueError:
        return False


def convert_to_wkt(geometry):
    """ convert a geometry (WKT or geoJson) to WKT
    Args:
        geometry : A string representing the geometry (WKT or geoJson)

    Returns:
        a valid WKT

    """

    try:
        # Check if the geometry is a valid WKT
        if is_valid_wkt(geometry):
            # Return the WKT
            return geometry
    except Exception:
        pass

    try:
        # Check if the geometry is a valid GeoJSON
        geojson_data = json.loads(geometry)
        geom = shape(geojson_data)
        return geom.wkt
    except ValueError:
        # Geometry is not a valid GeoJSON
        return None

def get_s3_uri_path(local_path: str, bucket_name:str = None) -> str:
    """Get the s3 path of the uploaded element (file or folder)

    Args:
      local_path(str): The local path of the uploaded folder/file on s3
      bucket_name(str): The optional bucket name set to store the file on s3

    Returns:
      str: the s3 uri of the uploaded folder/file
    """
    # get bucket name
    if bucket_name is None:
        bucket_name = os.getenv("AWS_BUCKET_NAME")  # careful, bucket name can still be None

    s3_key = os.path.basename(local_path)
    s3_uri = f"s3://{bucket_name}/{s3_key}"

    return s3_uri
