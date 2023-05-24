# This file contains functions for interacting with Google Cloud Storage.
from google.cloud import storage
from ga4_data_import.common import get_project_number


def add_bucket_read_access(
    project_id: str,
    bucket_name: str,
):
    """
    Add read access to the bucket for the compute service account.

    Args:
        project_id: The project id.
        bucket_name: The name of the bucket to add read access to.
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    policy = bucket.get_iam_policy(requested_policy_version=3)

    project_number = get_project_number(project_id)
    policy.bindings.append(
        {
            "role": "roles/storage.objectViewer",
            "members": [
                f"serviceAccount:{project_number}-compute@developer.gserviceaccount.com"
            ],
        }
    )
    bucket.set_iam_policy(policy)
