import logging
from geosyspy import Geosys
from geosyspy.utils.constants import SatelliteImageryCollection
import xarray
from datetime import datetime
import tempfile
import os

from analytics_datacube.utils import convert_to_wkt

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AnalyticsDatacube:

    def __init__(self, client_id: str,
                 client_secret: str,
                 username: str,
                 password: str,
                 enum_env: enumerate,
                 enum_region: enumerate,
                 priority_queue: str = "realtime",
                 ):
        self.region: str = enum_region.value
        self.env: str = enum_env.value
        self.priority_queue: str = priority_queue
        self.__client: Geosys = Geosys(client_id, client_secret, username, password, enum_env, enum_region,
                                       priority_queue)

    def generate_analytics_datacube(self,
                                    polygon,
                                    start_date: datetime.date,
                                    end_date: datetime.date,
                                    indicators: [str]):
        """
            Get a xarray.Dataset with indicators values for each pixel and for each date of images found between start and end dates.

            Args:
                - polygon: WKT/geoJson
                - start_date: beginning of the period
                - end_date: end of the period
                - indicators : list of indicators to get, among : ndvi, evi, gndvi, ndwi, cvi, cvin, lai

            Returns:
                xarray.Dataset
        """
        # validate and convert the geometry to WKT
        geometry = convert_to_wkt(polygon)

        if geometry is None:
            raise ValueError("The geometry is not a valid WKT of GeoJson")

        # Build a list with datasets of each indicator
        indicators_datasets = []
        for indicator in indicators:
            try:
                logging.info(f"AnalyticsDatacube:get_analytics_datacube: Get dataset for indicator {indicator}")
                indicator_dataset = self.__client.get_satellite_image_time_series(geometry, start_date, end_date,
                                                                                  collections=[
                                                                                      SatelliteImageryCollection.SENTINEL_2,
                                                                                      SatelliteImageryCollection.LANDSAT_8],
                                                                                  indicators=[indicator])
                indicators_datasets.append(indicator_dataset)
            except Exception as exc:
                logging.error(f"Error while generating dataset for {indicator} indicator: {str(exc)}")

        # Return merge of all datasets
        logging.info("AnalyticsDatacube:get_analytics_datacube: Create datacube by merging all indicators datasets")

        try:
            analytics_datacube = xarray.merge(indicators_datasets)
            return analytics_datacube

        except Exception as exc:
            logging.error(f"Error while merging results in the analytics datacube: {str(exc)}")
