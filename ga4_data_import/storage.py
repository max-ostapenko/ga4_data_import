from google.cloud import storage


def add_bucket_read_access(
    project_id,
    bucket_name
):
    
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    policy = bucket.get_iam_policy(requested_policy_version=3)

    compute_service_account_email = f"{project_id}-compute@developer.gserviceaccount.com"
    policy.bindings.append(
        {
            "role": "roles/storage.objectViewer",
            "members": [f"serviceAccount:{compute_service_account_email}"],
        }
    )
    bucket.set_iam_policy(policy)
