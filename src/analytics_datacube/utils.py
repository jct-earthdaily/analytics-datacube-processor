import logging
import xarray
from datetime import datetime
import tempfile
import os
import json
from shapely import wkt
from shapely.geometry import shape


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def dataset_to_zarr_format(dataset: xarray.Dataset):
    """
        Save a xarray.Dataset as zarr format in a temporary folder.
        Output zarr path : "Year-Month-Day_Hour-Minute-Second_analytics-datacube.zarr"

        Args:
            - dataset: the Dataset to save

        Returns:
            The complete zarr path
    """
    # Make a valid path whatever the OS
    zarr_path = os.path.join(tempfile.gettempdir(),
                             datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_analytics-datacube.zarr")
    logging.info("AnalyticsDatacube:save_dataset_to_temporary_zarr: path is " + zarr_path)

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
        # check if the geometry is a valid WKT
        if is_valid_wkt(geometry):
            # return the wkt
            return geometry
    except:
        try:
            # check if the geometry is a valid geoJson
            geojson_data = json.loads(geometry)
            geom = shape(geojson_data)
            geometry = geom.wkt

            return geometry

        except ValueError:
            # geometry is not a valid geoJson
            return None
