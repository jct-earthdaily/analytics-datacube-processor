import logging
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html

from analytics_datacube.utils import dataset_to_zarr_format
from api.constants import CloudStorageProvider, Indicator
from cloud_storage import cloud_storage_aws, cloud_storage_azure
from fastapi.staticfiles import StaticFiles
from geosyspy.geosys import Region, Env
from pydantic import BaseModel
import datetime as dt

from analytics_datacube.processor import AnalyticsDatacube

app = FastAPI(
    docs_url=None,
    title="AnalyticsDatacube" + " API",
    description="Api to create an Analytics Datacube of clear images"
)
app.mount("/static", StaticFiles(directory="./api/files"), name="static")


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AnalyticsDatacube" + " API",
        swagger_favicon_url="/static/favicon.svg"
    )


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

load_dotenv()


class Item(BaseModel):
    polygon: str
    startDate: dt.date
    endDate: dt.date


@app.post("/analytics-datacube", tags=["Analytic Computation"])
async def create_analytics_datacube(item: Item, cloud_storage_provider: CloudStorageProvider,
                                    indicators: List[Indicator] = Query(...)):
    # Initialize the client and test the connection
    API_CLIENT_ID = os.getenv('API_CLIENT_ID')
    API_CLIENT_SECRET = os.getenv('API_CLIENT_SECRET')
    API_USERNAME = os.getenv('API_USERNAME')
    API_PASSWORD = os.getenv('API_PASSWORD')

    client = AnalyticsDatacube(API_CLIENT_ID, API_CLIENT_SECRET, API_USERNAME, API_PASSWORD, Env.PROD, Region.NA)
    start_date = dt.datetime(item.startDate.year, item.startDate.month, item.startDate.day)
    end_date = dt.datetime(item.endDate.year, item.endDate.month, item.endDate.day)

    # generate analytics datacube
    analytics_datacube = client.generate_analytics_datacube(polygon=item.polygon, start_date=start_date, end_date=end_date,
                                                            indicators=[indicator.value for indicator in indicators])

    # convert the generated datacube in zarr file
    zarr_path = dataset_to_zarr_format(analytics_datacube)

    try:
        # upload result on chosen CloudStorage provider (AWS or Azure)
        if cloud_storage_provider == CloudStorageProvider.AWS and cloud_storage_aws.upload_folder_to_aws_s3(zarr_path):
            logger.info("Analytics DataCube uploaded to AWS S3")
            return {"storage_link": cloud_storage_aws.get_s3_uri_path(zarr_path)}
        elif cloud_storage_provider == CloudStorageProvider.AZURE and cloud_storage_azure.upload_directory_to_azure_blob_storage(
                zarr_path):
            logger.info("Analytics DataCube uploaded to Azure Blob Storage")
            return {"storage_link": cloud_storage_azure.get_azure_blob_url_path(zarr_path)}
    except Exception as exc:
        logging.error(f"Error while uploading folder to {cloud_storage_provider.value}: {exc}")
        raise HTTPException(status_code=500, detail=f"Error while uploading folder to {cloud_storage_provider.value} : {exc}")
