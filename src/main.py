"""analytics_datacube_processor main"""

import os
import argparse
from dotenv import load_dotenv

from byoa.cloud_storage import aws_s3
from geosyspy.geosys import Region, Env
from geosyspy.utils.jwt_validator import check_token_validity
from utils.file_utils import load_input_data
from analytics_datacube_processor.processor import AnalyticsDatacube
from analytics_datacube_processor.utils import dataset_to_zarr_format, get_s3_uri_path


def main(input_path=None, bearer_token=None, aws_s3_bucket_name=None):
    """_summary_

    Args:
        input_path (str, optional): path of the input file. Defaults to None.
        bearer_token (str, optional): bearer token to connect ro geosys API. Defaults to None.
        aws_s3_bucket_name (str, optional): bucket name to store the output file. Defaults to None.
    

    Returns:
        zarr_path: path of the output zarr file
    """

    load_dotenv()
    environment = os.getenv('APP_ENVIRONMENT', 'local')

    if environment == 'local':
        input_data = load_input_data(os.getenv('INPUT_JSON_PATH'))

    elif environment in ['integration', 'validation', 'production']:
        if not input_path:
            raise ValueError(f"No input path provided in the '{environment}' environment.")
        input_data = load_input_data(input_path)
    else:
        raise ValueError(f'Unrecognized environment: {environment}')

    api_client_id = os.getenv('API_CLIENT_ID')
    api_client_secret = os.getenv('API_CLIENT_SECRET')
    api_username = os.getenv('API_USERNAME')
    api_password = os.getenv('API_PASSWORD')
    public_certificate_key = os.getenv("CIPHER_CERTIFICATE_PUBLIC_KEY")
    if public_certificate_key is not None:
        public_certificate_key = public_certificate_key.replace("\\n", "\n")

    # Check token validity
    if bearer_token and (public_certificate_key is not None and not check_token_validity(bearer_token, public_certificate_key)):
        raise ValueError("Not Authorized")

    processor = AnalyticsDatacube(input_data, api_client_id, api_client_secret, api_username, api_password, Env.PROD,
                                  Region.NA, bearer_token=bearer_token)

    result = processor.trigger()
    zarr_path = dataset_to_zarr_format(result)
    if aws_s3_bucket_name:
        if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
            raise ValueError("Missing AWS credentials")
        try:
            # upload result on chosen CloudStorage provider (AWS or Azure)
            aws_s3.write_folder_to_aws_s3(zarr_path, bucket_name=aws_s3_bucket_name)
            zarr_path = get_s3_uri_path(zarr_path, bucket_name=aws_s3_bucket_name)
        except Exception as exc:
            raise RuntimeError(f"Error while uploading folder to AWS S3: {exc}") from exc

    print(f'output_file: {zarr_path}')
    return zarr_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, help='Path to the input data', default=None)
    parser.add_argument('--bearer_token', type=str, help='Geosys Api bearer token ', default=None)
    parser.add_argument('--aws_s3_bucket_name',type=str, help='AWS S3 Bucket name ', default=None)
    args = parser.parse_args()

    main(args.input_path, args.bearer_token, args.aws_s3_bucket_name)
