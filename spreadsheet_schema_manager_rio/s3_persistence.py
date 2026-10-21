import uniserde
from uniserde import ObjectId
from typing import Type
import boto3
import io
import urllib3
import asyncio

from .data_models import *
from . import constants


class S3Persistence:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        connection_string: str,
        bucket_name: str,
    ) -> None:
        # Suppress insecure request warnings (since verify=False will trigger them)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.s3_client = boto3.client(
            's3',
            endpoint_url=connection_string,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            verify=False  # Skips SSL certificate validation
        )
        self.bucket_name = bucket_name

    async def save_file(self, file_obj: io.BytesIO, s3_obj: str) -> None:
        await asyncio.to_thread(
            self.s3_client.upload_fileobj,
            file_obj,
            self.bucket_name,
            s3_obj,
        )

    async def get_file(self, s3_obj: str) -> io.BytesIO:
        file_obj = io.BytesIO()
        await asyncio.to_thread(
            self.s3_client.download_fileobj,
            self.bucket_name,
            s3_obj,
            file_obj,
        )
        file_obj.seek(0)
        return file_obj
    
    async def delete_file(self, s3_obj: str) -> None:
        await asyncio.to_thread(
            self.s3_client.delete_object,
            Bucket=self.bucket_name,
            Key=s3_obj,
        )
