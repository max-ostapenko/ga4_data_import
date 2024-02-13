"""
This file contains functions for interacting with Google Cloud Storage.
"""

from google.api_core import exceptions as core_exceptions
from google.cloud.storage import Client as StorageClient  # type: ignore


def create_bucket(
    bucket_name: str,
    region: str,
):
    """
    Create a new bucket with the provided name in the provided project.

    Args:
        project_id: The project id.
        bucket_name: The name of the bucket to create.
        region: The region to create the bucket in.
    """
    client = StorageClient()

    try:
        bucket = client.get_bucket(bucket_name)
    except core_exceptions.NotFound:
        bucket = client.bucket(bucket_name)
        bucket.storage_class = "STANDARD"
        client.create_bucket(bucket, location=region)


def add_bucket_read_access(
    bucket_name: str,
    service_account_email: str,
):
    """
    Add read access to the bucket for the compute service account.

    Args:
        project_id: The project id.
        bucket_name: The name of the bucket to add read access to.
    """
    client = StorageClient()
    bucket = client.get_bucket(bucket_name)
    policy = bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings.append(
        {
            "role": "roles/storage.objectViewer",
            "members": [f"serviceAccount:{service_account_email}"],
        }
    )
    bucket.set_iam_policy(policy)
