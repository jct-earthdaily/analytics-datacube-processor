""" Processor class """

import os
import time
import warnings
from datetime import datetime
from typing import Optional

import numpy as np
import psutil
import xarray
from byoa.telemetry.log_manager.log_manager import LogManager
from geosyspy import Geosys
from geosyspy.utils.constants import Env, Region, SatelliteImageryCollection

from analytics_datacube_processor.cloud_storage_provider import CloudStorageProvider
from analytics_datacube_processor.utils import (
    check_cloud_storage_provider_credentials,
    convert_to_wkt,
    dataset_to_zarr_format,
    delete_local_directory,
    upload_to_cloud_storage,
)
from schemas.output_schema import Metrics, OutputModel
from utils.file_utils import validate_data

warnings.simplefilter(action="ignore", category=UserWarning)
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
        entity_id: optional entity id to build the output path
        metrics: bool to provie metrics info in output (bandwitdh, duration)
        cloud_storage_provider: AWS S3/Azure Blob Storage
        clean_local_file: keep or delete temporary local file (zarr file)
    """

    def __init__(
        self,
        input_data,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        bearer_token: Optional[str] = None,
        entity_id: Optional[str] = None,
        aws_s3_bucket: Optional[str] = None,
        enum_env: Env = Env.PROD,
        enum_region: Region = Region.NA,
        priority_queue: str = "realtime",
        metrics: bool = False,
        cloud_storage_provider: CloudStorageProvider = CloudStorageProvider.AWS,
        clean_local_file=True,
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
        self.entity_id = entity_id
        self.metrics = metrics
        self.cloud_storage_provider = cloud_storage_provider
        self.aws_s3_bucket = aws_s3_bucket
        self.clean_local_file = clean_local_file
        self.zarr_path = None

    def prepare_data(self):
        """data preparation"""

        # Check if cloud storage provider credentials have been set
        check_cloud_storage_provider_credentials(self.cloud_storage_provider)
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

        # Build a list with datasets of each indicator
        indicators_datasets = []
        for indicator in input_data["indicators"]:
            try:
                logger.info(
                    f"AnalyticsDatacube: get_analytics_datacube: Get dataset for indicator {indicator}"
                )
                indicator_dataset = self.__client.get_satellite_image_time_series(
                    polygon=geometry,
                    start_date=datetime.fromisoformat(input_data["parameters"]["startDate"]),
                    end_date=datetime.fromisoformat(input_data["parameters"]["endDate"]),
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
            logger.error(f"Error while merging results in the analytics datacube: {str(exc)}")
            raise RuntimeError(
                f"Error while merging results in the analytics datacube: {str(exc)}"
            ) from exc

    def trigger(self):
        """trigger the processor
        Returns:
            output_schema object
        """
        logger.info("Processor triggered")
        start_time = time.time()

        bandwidth_init = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        self.prepare_data()

        datacube = self.predict(self.input_data)
        datacube = datacube.load()
        zarr_path = dataset_to_zarr_format(datacube)

        if self.entity_id:
            # Rename zarr file
            new_name = f"{self.entity_id}_{os.path.basename(zarr_path)}"
            new_path = os.path.join(os.path.dirname(zarr_path), new_name)
            os.rename(zarr_path, new_path)
            zarr_path = new_path

        # bandwidth use retrieval
        bandwidth_generation = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )

        # upload zarr file on the chosen cloud storage provider
        cloud_storage_link = upload_to_cloud_storage(
            self.cloud_storage_provider, zarr_path, self.aws_s3_bucket
        )

        self.zarr_path = zarr_path
        if self.clean_local_file:
            # delete tmp files
            delete_local_directory(zarr_path)

        # bandwidth_upload retrieval
        bandwidth_upload = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )

        # format result
        result = OutputModel(storage_links=cloud_storage_link)

        # adding metrics
        if self.metrics:
            metrics = Metrics(
                execution_time=f"{int(np.round((time.time() - start_time) / 60))} minutes {int(np.round(np.round((time.time() - start_time)) % 60))} seconds",
                data_generation_network_use=f"{np.round((bandwidth_generation - bandwidth_init) / 1024. / 1024. / 1024. * 8, 3)} Gb",
                data_upload_network_use=f"{np.round((bandwidth_upload - bandwidth_generation) / 1024. / 1024. / 1024. * 8, 3)} Gb",
            )
            result.metrics = metrics

        # validate output data
        # validate_data(result.model_dump(), "output")

        return result.model_dump()
