"""Fast api to trigger the analytics datacube processor.
Result can be stored on AWS S3 or Azure Blob storage 

Returns:
    storage_link: path of the output zarr file
"""

import os
import shutil

from typing import List
from typing import Annotated

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from byoa.cloud_storage import aws_s3, azure_blob_storage
from byoa.telemetry.log_manager.log_manager import LogManager
from geosyspy.utils.jwt_validator import check_token_validity

from api.constants import CloudStorageProvider, Indicator
from schemas.input_schema import Parameters, InputModel
from analytics_datacube_processor.processor import AnalyticsDatacube
from analytics_datacube_processor.utils import get_s3_uri_path, dataset_to_zarr_format

logger_manager = LogManager.get_instance()
load_dotenv()

app = FastAPI(
    docs_url=None, title="analytics_datacube_processor" + " API", description=""
)

# identity server configuration
tokenUrl = os.getenv("IDENTITY_SERVER_URL")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)
app.mount("/static", StaticFiles(directory="./api/files"), name="static")
public_certificate_key = os.getenv("CIPHER_CERTIFICATE_PUBLIC_KEY")
if public_certificate_key is not None:
    public_certificate_key = public_certificate_key.replace("\\n", "\n")

# pylint: disable=missing-docstring


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html() -> str:
    """
    Generate HTML code for Swagger UI.

    Returns:
        str: The HTML code for the Swagger UI.

    Notes:
        This function generates HTML code for the Swagger UI user interface,
        used to visualize and interact with the AnalyticsDatacubeProcessor API.
        It includes the OpenAPI API URL, API title, and favicon URL.

        Example:
            html_code = await swagger_ui_html()
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AnalyticsDatacubeProcessor" + " API",
        swagger_favicon_url="/static/favicon.svg",
    )


@app.post("/analytics-datacube", tags=["Analytic Computation"])
async def create_analytics_datacube(
    token: Annotated[str, Depends(oauth2_scheme)],
    parameters: Parameters,
    cloud_storage_provider: CloudStorageProvider,
    aws_s3_bucket: str = None,
    indicators: List[Indicator] = Query(...),
):
    # Check token validity
    if not token or (
        public_certificate_key is not None
        and not check_token_validity(token, public_certificate_key)
    ):
        raise HTTPException(status_code=401, detail="Not Authorized")

    try:
        input_data = InputModel(
            parameters=parameters,
            indicators=[indicator.value for indicator in indicators],
        )

        # Check if cloud storage provider credentials have been set
        __check_cloud_storage_provider_credentials(cloud_storage_provider)

        # Init the processor
        client = AnalyticsDatacube(input_data.model_dump(), bearer_token=token)

        # Generate analytics datacube & convert result in zarr format
        result = client.trigger()
        zarr_path = dataset_to_zarr_format(result)

        if not zarr_path:
            logger_manager.error("Error while generating datacube")
            raise HTTPException(status_code=500)

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error while generating datacube: {exc}"
        ) from exc
    # Upload result on chosen CloudStorage provider (AWS or Azure)
    return upload_to_cloud_storage(cloud_storage_provider, zarr_path, aws_s3_bucket)


def upload_to_aws_s3(zarr_path: str, aws_s3_bucket: str):
    """
    Uploads data to AWS S3.

    Args:
        zarr_path (str): The path to the data to be uploaded.
        aws_s3_bucket (str): The AWS S3 bucket name.

    Returns:
        dict or None: A dictionary containing the storage link if the upload is successful,
                      otherwise None.

    Notes:
        This function uploads data to AWS S3 and returns a dictionary containing the storage link.
        If the upload fails, it returns None.
    """
    if aws_s3.write_folder_to_aws_s3(zarr_path, aws_s3_bucket):
        logger_manager.info("Analytics DataCube uploaded to AWS S3")
        return {"storage_link": get_s3_uri_path(zarr_path, aws_s3_bucket)}


def upload_to_azure_blob_storage(zarr_path: str):
    """
    Uploads data to Azure Blob Storage.

    Args:
        zarr_path (str): The path to the data to be uploaded.

    Returns:
        dict or None: A dictionary containing the storage link if the upload is successful,
                      otherwise None.

    Notes:
        This function uploads data to Azure Blob Storage and returns a dictionary containing the storage link.
        If the upload fails, it returns None.
    """
    if azure_blob_storage.upload_directory_to_azure_blob_storage(zarr_path):
        logger_manager.info("Analytics DataCube uploaded to Azure Blob Storage")
        return {"storage_link": azure_blob_storage.get_azure_blob_url_path(zarr_path)}


def upload_to_cloud_storage(
    cloud_storage_provider: CloudStorageProvider,
    zarr_path: str,
    aws_s3_bucket: str = None,
):
    """
    Uploads data to the specified cloud storage provider.

    Args:
        cloud_storage_provider (CloudStorageProvider): The cloud storage provider (AWS or Azure).
        zarr_path (str): The path to the data to be uploaded.
        aws_s3_bucket (str, optional): The AWS S3 bucket name. Required only if cloud_storage_provider is AWS.

    Returns:
        dict or None: A dictionary containing the storage link if the upload is successful,
                      otherwise None.

    Notes:
        This function uploads data to the specified cloud storage provider based on the provider type.
        If the upload fails, it returns None.
    """
    try:
        if cloud_storage_provider == CloudStorageProvider.AWS:
            if aws_s3.write_folder_to_aws_s3(zarr_path, aws_s3_bucket):
                logger_manager.info("Analytics DataCube uploaded to AWS S3")
                return {"storage_link": get_s3_uri_path(zarr_path, aws_s3_bucket)}
        elif cloud_storage_provider == CloudStorageProvider.AZURE:
            if azure_blob_storage.upload_directory_to_azure_blob_storage(zarr_path):
                logger_manager.info("Analytics DataCube uploaded to Azure Blob Storage")
                return {
                    "storage_link": azure_blob_storage.get_azure_blob_url_path(
                        zarr_path
                    )
                }
    except Exception as exc:
        logger_manager.error(
            f"Error while uploading folder to {cloud_storage_provider.value}: {exc}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error while uploading folder to {cloud_storage_provider.value}: {exc}",
        ) from exc


def __delete_local_directory(path: str):
    """
    Delete a local directory if it exists.

    Args:
        path (str): The path of the directory to delete.
    """
    # Remove local csv file
    if os.path.exists(path):
        logger_manager.info("Delete local directory after upload")
        shutil.rmtree(path)
    else:
        logger_manager.info("File not present.")


def __check_cloud_storage_provider_credentials(
    cloud_storage_provider: CloudStorageProvider,
):
    """
    Check the credentials for the specified cloud storage provider.

    Args:
        cloud_storage_provider (CloudStorageProvider): The cloud storage provider (AWS or Azure).

    Raises:
        HTTPException: If the credentials for the specified cloud storage provider are missing.
    """
    # Check Azure credentials
    if cloud_storage_provider == CloudStorageProvider.AZURE:
        if not (
            os.getenv("AZURE_ACCOUNT_NAME")
            and os.getenv("AZURE_SAS_CREDENTIAL")
            and os.getenv("AZURE_BLOB_CONTAINER_NAME")
        ):
            raise HTTPException(status_code=400, detail="Missing Azure credentials")

    # Check AWS credentials
    if cloud_storage_provider == CloudStorageProvider.AWS:
        if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
            raise HTTPException(status_code=400, detail="Missing AWS credentials")
