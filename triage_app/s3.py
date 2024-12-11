import boto3
from botocore import client
import traceback


class S3Manager:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self._client = None

    def get_client(self):
        if not self._client:
            try:
                self._client = boto3.client('s3', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name, config=client.Config(signature_version='s3v4'))
            except:
                traceback.print_exc()
                return None
        return self._client

    def reset_client(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self._client = None  # Force reinitialization on the next get_client call
