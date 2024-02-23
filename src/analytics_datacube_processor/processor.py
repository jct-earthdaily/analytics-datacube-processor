""" Processor class """
import logging
from datetime import datetime
from byoa.telemetry.log_manager.log_manager import LogManager

import xarray
from geosyspy import Geosys
from geosyspy.utils.constants import SatelliteImageryCollection, Env, Region
from analytics_datacube_processor.utils import convert_to_wkt
from utils.file_utils import validate_data

logger = LogManager.get_instance()

class AnalyticsDatacube:
    """AnalyticsDatacube is the main client class processor to build the datacube

    `client = Geosys(api_client_id, api_client_secret, api_username, api_password, env, region)`

    Parameters:
        input_data: dict of input data
        enum_env: 'Env.PROD' or 'Env.PREPROD'
        enum_region: 'Region.NA'
        priority_queue: 'realtime' or 'bulk'
        bearer_token: optional geosys identity server token to access geosys api
    """

    def __init__(
        self,
        input_data,
        client_id: str = None,
        client_secret: str = None,
        username: str = None,
        password: str = None,
        enum_env: Env = Env.PROD,
        enum_region: Region = Region.NA,
        priority_queue: str = "realtime",
        bearer_token: str = None,
    ):
        validate_data(input_data, "input")
        self.input_data = input_data
        self.priority_queue: str = priority_queue
        self.__client: Geosys = Geosys(
            client_id,
            client_secret,
            username,
            password,
            enum_env,
            enum_region,
            priority_queue,
            bearer_token,
        )

    def prepare_data(self):
        """data preparation"""
        logger.info("data_prepared")

    def predict(self, input_data):
        """
        predict data
        Args:
            input_data (dict): dict of input data

        Raises:
            ValueError: when an invalid geometry is provided as input

        Returns:
            xarray dataset
        """
        # validate and convert the geometry to WKT
        geometry = convert_to_wkt(input_data["parameters"]["polygon"])

        if geometry is None:
            raise ValueError("The geometry is not a valid WKT of GeoJson")

        # Build a list with datasets of each indicator
        indicators_datasets = []
        for indicator in input_data["indicators"]:
            try:
                logger.info(
                    f"AnalyticsDatacube: get_analytics_datacube: Get dataset for indicator {indicator}"
                )
                indicator_dataset = self.__client.get_satellite_image_time_series(
                    geometry,
                    datetime.fromisoformat(input_data["parameters"]["startDate"]),
                    datetime.fromisoformat(input_data["parameters"]["endDate"]),
                    collections=[
                        SatelliteImageryCollection.SENTINEL_2,
                        SatelliteImageryCollection.LANDSAT_8,
                    ],
                    indicators=[indicator],
                )
                indicators_datasets.append(indicator_dataset)
            except Exception as exc:
                logger.error(
                    f"Error while generating dataset for {indicator} indicator: {str(exc)}"
                )

        # Return merge of all datasets
        logger.info(
            "AnalyticsDatacube:get_analytics_datacube: Create datacube by merging all "
            "indicators datasets"
        )

        try:
            analytics_datacube = xarray.merge(indicators_datasets)
            return analytics_datacube

        except Exception as exc:
            logger.error(
                f"Error while merging results in the analytics datacube: {str(exc)}"
            )
            raise RuntimeError(
                f"Error while merging results in the analytics datacube: {str(exc)}"
            ) from exc

    def trigger(self):
        """trigger the processor
        Returns:
            xarray dataset
        """
        logger.info("Processor triggered")

        self.prepare_data()

        result = self.predict(self.input_data)

        return result
