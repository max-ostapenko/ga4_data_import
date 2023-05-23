
from google.cloud import resource_manager

def get_project_number(project_id):
    client = resource_manager.Client()
    projects = client.list_projects()
    for project in projects:
        if project.name == project_id:
            return project.number
    return None
