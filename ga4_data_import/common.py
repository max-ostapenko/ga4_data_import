from google.cloud import resourcemanager_v3
from google.cloud import compute_v1


def get_project_number(project_id):
    """
    Get the project number from the project id.
    :param project_id: The project id.
    :return: The project number.
    """
    client = resourcemanager_v3.ProjectsClient()
    request = resourcemanager_v3.SearchProjectsRequest(query=f"id:{project_id}")
    response = client.search_projects(request=request)
    page_result = client.search_projects(request=request)
    for response in page_result:
        if response.project_id == project_id:
            project = response.name
            return project.replace("projects/", "")


def get_region_from_zone(zone):
    parts = zone.split("-")
    region = "-".join(parts[:-1])
    return region


def wait_for_operation(
    operation: compute_v1.Operation, project_id: str
) -> compute_v1.Operation:
    """
    This method waits for an operation to be completed. Calling this function
    will block until the operation is finished.

    Args:
        operation: The Operation object representing the operation you want to
            wait on.
        project_id: project ID or project number of the Cloud project you want to use.

    Returns:
        Finished Operation object.
    """
    kwargs = {"project": project_id, "operation": operation.name}
    if operation.zone:
        client = compute_v1.ZoneOperationsClient()
        # Operation.zone is a full URL address of a zone, so we need to extract just the name
        kwargs["zone"] = operation.zone.rsplit("/", maxsplit=1)[1]
    elif operation.region:
        client = compute_v1.RegionOperationsClient()
        # Operation.region is a full URL address of a region, so we need to extract just the name
        kwargs["region"] = operation.region.rsplit("/", maxsplit=1)[1]
    else:
        client = compute_v1.GlobalOperationsClient()
    return client.wait(**kwargs)
