"""Common functions for the GA4 Data Import API code samples."""

from google.cloud.resourcemanager_v3 import (ProjectsClient,
                                             SearchProjectsRequest)


def get_project_number(project_id: str):
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

    return ""
