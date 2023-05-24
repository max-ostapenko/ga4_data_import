"""Common functions for the GA4 Data Import API code samples."""

from google.cloud.resourcemanager_v3 import (
    ProjectsClient,
    SearchProjectsRequest,
)


def get_project_number(project_id):
    """
    Get the project number from the project id.

    Args:
        project_id: The project id to get the project number from.
    Returns:
        str, The project number.
    """
    request = SearchProjectsRequest(query=f"id:{project_id}")
    response = ProjectsClient().search_projects(request=request)
    page_result = ProjectsClient().search_projects(request=request)
    for response in page_result:
        if response.project_id == project_id:
            project = response.name
            return project.replace("projects/", "")


def get_region_from_zone(zone):
    """
    Get the region from the zone.

    Args:
        zone: The zone to get the region from.
    Returns:
        str, The region.
    """
    parts = zone.split("-")
    return "-".join(parts[:-1])


def read_pub_key(pub_key_path):
    with open(pub_key_path, "r") as file:
        return " ".join(file.read().strip().split(" ")[0:2])
