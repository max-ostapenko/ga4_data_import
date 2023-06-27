# Table of Contents

* [ga4\_data\_import](#ga4_data_import)
* [ga4\_data\_import.common](#ga4_data_import.common)
  * [get\_project\_number](#ga4_data_import.common.get_project_number)
* [ga4\_data\_import.compute](#ga4_data_import.compute)
  * [create\_static\_address](#ga4_data_import.compute.create_static_address)
  * [create\_instance](#ga4_data_import.compute.create_instance)
  * [add\_server\_pub\_key](#ga4_data_import.compute.add_server_pub_key)
* [ga4\_data\_import.storage](#ga4_data_import.storage)
  * [create\_bucket](#ga4_data_import.storage.create_bucket)
  * [add\_bucket\_read\_access](#ga4_data_import.storage.add_bucket_read_access)
* [ga4\_data\_import.workflow](#ga4_data_import.workflow)
  * [deploy\_workflow](#ga4_data_import.workflow.deploy_workflow)
  * [deploy\_scheduler](#ga4_data_import.workflow.deploy_scheduler)

<a id="ga4_data_import"></a>

# ga4\_data\_import

Google Analytics 4 Data Import pipeline using Google Cloud Platform.

<a id="ga4_data_import.common"></a>

# ga4\_data\_import.common

Common functions for the GA4 Data Import API code samples.

<a id="ga4_data_import.common.get_project_number"></a>

#### get\_project\_number

```python
def get_project_number(project_id: str)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/common.py#L9)

Get the project number from the project id.

**Arguments**:

- `project_id` - The project id to get the project number from.
  

**Returns**:

  str, The project number.

<a id="ga4_data_import.compute"></a>

# ga4\_data\_import.compute

This file contains functions for creating a Compute Engine instance and static address.

<a id="ga4_data_import.compute.create_static_address"></a>

#### create\_static\_address

```python
def create_static_address(project_id: str, region: str, instance_name: str)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/compute.py#L32)

Create a static address with the provided name, project id, and region.

**Arguments**:

- `project_id` - The project id.
- `region` - The region to create the address in.
- `instance_name` - The name of the instance.
  

**Returns**:

  str, The static address.

<a id="ga4_data_import.compute.create_instance"></a>

#### create\_instance

```python
def create_instance(instance_name: str,
                    project_id: str,
                    zone: str,
                    static_address: str,
                    bucket_name: str,
                    sftp_username: str,
                    service_account_email: str = "")
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/compute.py#L66)

Create a Compute Engine instance with the provided name, project id, zone, and bucket name.

**Arguments**:

- `instance_name` - The name of the instance.
- `project_id` - The project id.
- `zone` - The zone to create the instance in.
- `static_address` - The static address to assign to the instance.
- `bucket_name` - The name of the bucket to mount on the instance.
- `sftp_username` - The username to create on the instance.
- `service_account_email` - The service account email to use as the
  instance's service account.
  

**Returns**:

  dict, The instance response.

<a id="ga4_data_import.compute.add_server_pub_key"></a>

#### add\_server\_pub\_key

```python
def add_server_pub_key(project_id: str, zone: str, instance_name: str,
                       pub_key: str, username: str)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/compute.py#L202)

Add the provided SSH public key to the instance metadata.

**Arguments**:

- `project_id` - The project id.
- `zone` - The zone to create the instance in.
- `instance_name` - The name of the instance.
- `pub_key` - SSH public key value to add to the instance metadata.
- `username` - The username to create on the instance.

<a id="ga4_data_import.storage"></a>

# ga4\_data\_import.storage

This file contains functions for interacting with Google Cloud Storage.

<a id="ga4_data_import.storage.create_bucket"></a>

#### create\_bucket

```python
def create_bucket(bucket_name: str, region: str)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/storage.py#L9)

Create a new bucket with the provided name in the provided project.

**Arguments**:

- `project_id` - The project id.
- `bucket_name` - The name of the bucket to create.
- `region` - The region to create the bucket in.

<a id="ga4_data_import.storage.add_bucket_read_access"></a>

#### add\_bucket\_read\_access

```python
def add_bucket_read_access(bucket_name: str, service_account_email: str)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/storage.py#L28)

Add read access to the bucket for the compute service account.

**Arguments**:

- `project_id` - The project id.
- `bucket_name` - The name of the bucket to add read access to.

<a id="ga4_data_import.workflow"></a>

# ga4\_data\_import.workflow

Workflow deployment module to configure BigQuery export to Cloud Storage.

<a id="ga4_data_import.workflow.deploy_workflow"></a>

#### deploy\_workflow

```python
def deploy_workflow(project_id, region, workflow_id, service_account_email)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/workflow.py#L20)

Deploy a workflow to the project.

**Arguments**:

- `project_id` - The project id.
- `region` - The region to deploy to.
- `workflow_id` - The workflow id.
- `service_account_email` - The service account email to use as the workflow's service account.

<a id="ga4_data_import.workflow.deploy_scheduler"></a>

#### deploy\_scheduler

```python
def deploy_scheduler(project_id, region, scheduler_id, service_account_email,
                     schedule, workflow_id, query, storage_path)
```

[[view_source]](https://github.com/max-ostapenko/ga4_data_import/blob/main/ga4_data_import/workflow.py#L90)

Deploy a trigger to the project.

**Arguments**:

- `project_id` - The project id.
- `region` - The region to deploy to.
- `scheduler_id` - The trigger id.
- `service_account_email` - The service account email to use as the
- `schedule` - The schedule for the trigger.
- `workflow_id` - The workflow id.
- `query` - The query to run.
- `storage_path` - The storage path to export to.

