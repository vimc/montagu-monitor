import boto3
import botocore


class S3Helper:
    def __init__(self):
        self.s3 = boto3.resource('s3')

    def get_bucket(self, bucket_id):
        bucket = self.s3.Bucket(bucket_id)
        try:
            self.s3.meta.client.head_bucket(Bucket=bucket_id)
            return bucket
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return None
            else:
                raise e
