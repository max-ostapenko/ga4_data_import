"""
Workflow deployment module to configure BigQuery export to Cloud Storage.
"""

import json

from google.cloud.scheduler_v1.services.cloud_scheduler.client import \
    CloudSchedulerClient
from google.cloud.scheduler_v1.types import (CreateJobRequest, HttpMethod,
                                             HttpTarget, Job)
from google.cloud.workflows_v1.services.workflows.client import WorkflowsClient
from google.cloud.workflows_v1.types import CreateWorkflowRequest, Workflow


def deploy_workflow(
    project_id,
    region,
    workflow_id,
    service_account_email,
):
    """
    Deploy a workflow to the project.

    Args:
        project_id: The project id.
        region: The region to deploy to.
        workflow_id: The workflow id.
        service_account_email: The service account email to use as the workflow's service account.
    """
    workflows_client = WorkflowsClient()

    # Read the workflow definition file
    workflow = Workflow(
        service_account=service_account_email,
        source_contents="""

main:
    params: [args]
    steps:
    - init:
        assign:
        - project_id: ${args.project_id}
        - query: ${args.query}
        - storage_path: ${args.storage_path}
    - query_data:
        call: googleapis.bigquery.v2.jobs.insert
        args:
            projectId: ${project_id}
            body:
                configuration:
                    query:
                        useLegacySql: false
                        flattenResults: true
                        query: ${query}
        result: queryResult
    - get_source_table:
        assign:
        - dataset_id: ${queryResult.configuration.query.destinationTable.datasetId}
        - table_id: ${queryResult.configuration.query.destinationTable.tableId}
    - export_table:
        call: googleapis.bigquery.v2.jobs.insert
        args:
            projectId: ${project_id}
            body:
                configuration:
                    extract:
                        destinationUri: ${storage_path}
                        destinationFormat: "csv"
                        sourceTable:
                            projectId: ${project_id}
                            datasetId: ${dataset_id}
                            tableId: ${table_id}
""",
    )

    request = CreateWorkflowRequest(
        parent=f"projects/{project_id}/locations/{region}",
        workflow=workflow,
        workflow_id=workflow_id,
    )

    workflows_client.create_workflow(request=request).result()


def deploy_scheduler(
    project_id,
    region,
    scheduler_id,
    service_account_email,
    schedule,
    workflow_id,
    query,
    storage_path,
):
    """
    Deploy a trigger to the project.

    Args:
        project_id: The project id.
        region: The region to deploy to.
        scheduler_id: The trigger id.
        service_account_email: The service account email to use as the
        schedule: The schedule for the trigger.
        workflow_id: The workflow id.
        query: The query to run.
        storage_path: The storage path to export to.
    """
    client = CloudSchedulerClient()
    job_arguments = json.dumps(
        {"project_id": project_id, "query": query, "storage_path": storage_path}
    )

    job = Job(
        name=f"projects/{project_id}/locations/{region}/jobs/{scheduler_id}",
        schedule=schedule,
        time_zone="Etc/UTC",
        http_target=HttpTarget(
            uri=f"https://workflowexecutions.googleapis.com/v1/projects/{project_id}/locations/{region}/workflows/{workflow_id}/executions",  # pylint: disable=line-too-long
            http_method=HttpMethod.POST,
            headers={
                "Content-Type": "application/json",
            },
            body=json.dumps({"argument": job_arguments}).encode(),
            oauth_token={
                "service_account_email": service_account_email,
            },
        ),
    )

    request = CreateJobRequest(
        parent=f"projects/{project_id}/locations/{region}",
        job=job,
    )

    client.create_job(request=request)
