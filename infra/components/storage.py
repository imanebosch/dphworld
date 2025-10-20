from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from config import StorageConfig
from constructs import Construct


class Storage(Construct):
    def __init__(self, scope: Construct, construct_id: str, config: StorageConfig):
        super().__init__(scope, construct_id)

        self.bucket = s3.Bucket(
            self,
            "Bucket",
            bucket_name=f"{config.name}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy[config.removal_policy],
            auto_delete_objects=True,
        )
