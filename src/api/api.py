"""Fast api to trigger the analytics datacube processor.
Result can be stored on AWS S3 or Azure Blob storage 

Returns:
    storage_link: path of the output zarr file
"""

import os
from typing import Annotated, List, Optional

from byoa.telemetry.log_manager.log_manager import LogManager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from geosyspy.utils.jwt_validator import check_token_validity

from analytics_datacube_processor.cloud_storage_provider import CloudStorageProvider
from analytics_datacube_processor.processor import AnalyticsDatacube
from api.constants import Indicator, Question
from schemas.input_schema import InputModel, Parameters

logger_manager = LogManager.get_instance()
load_dotenv()

app = FastAPI(docs_url=None, title="analytics_datacube_processor" + " API", description="")

# identity server configuration
tokenUrl = os.getenv("IDENTITY_SERVER_URL")
if tokenUrl is None:
    raise HTTPException(status_code=500, detail="No IDENTITY_SERVER_URL value is defined in env.")

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
    aws_s3_bucket: Optional[str] = None,
    indicators: List[Indicator] = Query(...),
    entity_id: str = "entity_1",
    metrics: Question = Query(
        alias="Display metrics information (bandwidth consumption, duration)"
    ),
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

        display_metrics = False
        if metrics == Question.YES:
            display_metrics = True

        # Init the processor
        client = AnalyticsDatacube(
            input_data.model_dump(),
            bearer_token=token,
            cloud_storage_provider=cloud_storage_provider,
            aws_s3_bucket=aws_s3_bucket,
            metrics=display_metrics,
            entity_id=entity_id,
        )

        # Generate analytics datacube
        result = client.trigger()

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error while generating datacube: {exc}"
        ) from exc
