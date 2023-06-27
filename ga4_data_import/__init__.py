"""
Google Analytics 4 Data Import pipeline using Google Cloud Platform.
"""

from ga4_data_import.common import get_project_number

from ga4_data_import.compute import (
    create_static_address,
    create_instance,
    add_server_pub_key,
)

from ga4_data_import.storage import create_bucket, add_bucket_read_access

from ga4_data_import.workflow import deploy_workflow, deploy_scheduler
