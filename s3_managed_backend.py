from typing import Dict, List

import boto3
from cdktf import S3Backend
from constructs import Construct

from sdvcf.tags import Tags
from dynamodb_lock import create_dynamodb_lock_table


class S3ManagedBackend(S3Backend):
    """
    An extension of the `S3Backend` that manages the creation and configuration of an S3 bucket for use as a backend.

    This class is responsible for ensuring that the specified S3 bucket exists within the given region and applies
    tags to the bucket based on the tags defined in the provided scope. If the bucket does not exist, it is created
    with the appropriate configuration.
    """

    def __init__(self, scope: Construct, region: str, bucket: str, key: str, encrypt: bool):
        s3 = boto3.client("s3", region_name=region)
        dynamodb_table = create_dynamodb_lock_table(region)
        buckets = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
        if bucket not in buckets:
            # https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLocation.html#API_GetBucketLocation_ResponseSyntax
            # us-east-1 is Null for LocationConstraint
            if region == "us-east-1":
                s3.create_bucket(
                    Bucket=bucket,
                )
            else:
                s3.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            tag_set: List[Dict[str, str]] = []
            for tag, value in Tags(scope, "backend").to_dict.items():
                tag_set.append({"Key": tag, "Value": value})
            s3.put_bucket_tagging(Bucket=bucket, Tagging={"TagSet": tag_set})
            s3.put_bucket_versioning(
                Bucket=bucket, VersioningConfiguration={"MFADelete": "Disabled", "Status": "Enabled"}
            )

        super().__init__(scope, region=region, bucket=bucket, key=key, encrypt=encrypt, dynamodb_table=dynamodb_table)
