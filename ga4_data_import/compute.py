# This file contains functions for creating a Compute Engine instance and static address.

from google.cloud.compute_v1.services.instances.client import InstancesClient
from google.cloud.compute_v1.services.addresses.client import AddressesClient
from google.cloud.compute_v1.types import (
    Address,
    AccessConfig,
    AttachedDisk,
    AttachedDiskInitializeParams,
    InsertAddressRequest,
    InsertInstanceRequest,
    Instance,
    Items,
    GetAddressRequest,
    Metadata,
    NetworkInterface,
    Scheduling,
    ServiceAccount,
    ShieldedInstanceConfig,
    ShieldedInstanceIntegrityPolicy,
    SetMetadataInstanceRequest,
    Tags,
)
from ga4_data_import.common import (
    get_project_number,
)


def create_static_address(project_id, region, instance_name):
    """
    Create a static address with the provided name, project id, and region.

    Args:
        project_id: The project id.
        region: The region to create the address in.
        instance_name: The name of the instance.
    Returns:
        str, The static address.
    """
    address_name = f"{instance_name}-static"
    address_request = GetAddressRequest(
        project=project_id, region=region, address=address_name
    )
    address_client = AddressesClient()

    try:
        # Check if the address already exists
        existing_address_response = address_client.get(address_request)
        return existing_address_response.address
    except:
        # Address does not exist, create a new one
        insert_address_request = InsertAddressRequest(
            project=project_id,
            region=region,
            address_resource=Address(name=address_name, network_tier="STANDARD"),
        )
        address_client.insert(insert_address_request).result()
        new_address_response = address_client.get(address_request)
        return new_address_response.address


def create_instance(
    instance_name,
    project_id,
    zone,
    static_address,
    bucket_name,
    sftp_username,
    service_account_email = None,
):
    """
    Create a Compute Engine instance with the provided name, project id, zone, and bucket name.
    
    Args:
        instance_name: The name of the instance.
        project_id: The project id.
        zone: The zone to create the instance in.
        static_address: The static address to assign to the instance.
        sftp_username: The username to create on the instance.
        bucket_name: The name of the bucket to mount on the instance.
    """

    # Create the instance request
    disk = AttachedDisk(
        auto_delete=True,
        boot=True,
        initialize_params=AttachedDiskInitializeParams(
            disk_size_gb=10,
            source_image="projects/debian-cloud/global/images/debian-11-bullseye-v20230509",
            disk_type=f"projects/{project_id}/zones/{zone}/diskTypes/pd-balanced",
        ),
    )

    metadata = [
        Items(
            key="startup-script",
            value=f"""#!/bin/bash
# Install gcsfuse
# https://cloud.google.com/storage/docs/gcsfuse-quickstart-mount-bucket#install
export GCSFUSE_REPO=gcsfuse-$(lsb_release -c -s)
echo "deb https://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
apt-get update -y
apt-get install -y fuse gcsfuse
rm -rf /var/lib/apt/lists/*

# Create SFTP user
adduser {sftp_username}

# Mount bucket
sudo -u {sftp_username} mkdir /home/{sftp_username}/{bucket_name}_mounted
sudo -u {sftp_username} gcsfuse -o ro --implicit-dirs --enable-storage-client-library {bucket_name} /home/{sftp_username}/{bucket_name}_mounted
chown root:root /home/{sftp_username}

# Configure SFTP server
sed -i "s/^Subsystem\tsftp.*/Subsystem\tsftp internal-sftp/" /etc/ssh/sshd_config
tee -a /etc/ssh/sshd_config << EOM
Match User {sftp_username}
\tForceCommand internal-sftp -d /{bucket_name}_mounted
\tChrootDirectory /home/%u
\tAllowTcpForwarding no
\tX11Forwarding no
\tPasswordAuthentication no
\tAuthenticationMethods publickey
EOM
systemctl restart ssh""",
        )
    ]

    network_interface = NetworkInterface(
        name=f"{instance_name}-nic0",
        access_configs=[
            AccessConfig(
                nat_i_p=static_address,
                network_tier="STANDARD",
            )
        ],
    )


    if not service_account_email:
        project_number = get_project_number(project_id)
        service_account_email = f"{project_number}-compute@developer.gserviceaccount.com"
    service_account = ServiceAccount(
        email=service_account_email,
        scopes=[
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring.write",
            "https://www.googleapis.com/auth/servicecontrol",
            "https://www.googleapis.com/auth/service.management.readonly",
            "https://www.googleapis.com/auth/trace.append",
        ],
    )

    insert_instance_request = InsertInstanceRequest(
        project=project_id,
        zone=zone,
        instance_resource=Instance(
            disks=[disk],
            machine_type=f"projects/{project_id}/zones/{zone}/machineTypes/f1-micro",
            name=instance_name,
            network_interfaces=[network_interface],
            metadata=Metadata(items=metadata),
            scheduling=Scheduling(
                automatic_restart=True,
                on_host_maintenance="MIGRATE",
                preemptible=False,
                provisioning_model="STANDARD",
            ),
            service_accounts=[service_account],
            shielded_instance_config=ShieldedInstanceConfig(
                enable_secure_boot=False,
                enable_vtpm=True,
                enable_integrity_monitoring=True,
            ),
            tags=Tags(items=["default-allow-ssh"]),
            shielded_instance_integrity_policy=ShieldedInstanceIntegrityPolicy(
                update_auto_learn_policy=True
            ),
            ignore_unknown_fields=True,
        ),
        ignore_unknown_fields=True,
    )

    # Create the instance
    InstancesClient().insert(request=insert_instance_request).result()
    instance_response = InstancesClient().get(project=project_id, zone=zone, instance=instance_name)

    return instance_response


def add_server_pub_key(
    project_id,
    zone,
    instance_name,
    key,
    sftp_username,
):
    """
    Add the provided SSH public key to the instance metadata.

    Args:
        project_id: The project id.
        zone: The zone to create the instance in.
        instance_name: The name of the instance.
        sftp_username: The username to create on the instance.
        key: SSH public key value
    Returns:
        None
    """

    instance_response = InstancesClient().get(
        project=project_id, zone=zone, instance=instance_name
    )

    metadata_items = instance_response.metadata.items
    existing_ssh_keys = ""
    new_key = sftp_username.strip() + ":" + key.strip()
    for item_index in range(len(metadata_items)):
        if metadata_items[item_index].key == "ssh-keys":
            existing_ssh_keys = metadata_items[item_index].value.split("\n")

            # Check if the key already exists
            need_append = True
            for key_index in range(len(existing_ssh_keys)):
                existing_ssh_keys[key_index] = existing_ssh_keys[key_index].strip()
                if existing_ssh_keys[key_index] == new_key:
                    need_append = False
                    break

            existing_ssh_keys = "\n".join(existing_ssh_keys)

            # Update the instance metadata with the new SSH key
            if need_append:
                metadata_items[item_index].value = (
                    existing_ssh_keys + "\n" + new_key
                )
            break

    if not existing_ssh_keys:
        metadata_items.append(Items(key="ssh-keys", value=new_key))

    request = SetMetadataInstanceRequest(
        project=project_id,
        zone=zone,
        instance=instance_name,
        metadata_resource=Metadata(
            fingerprint=instance_response.metadata.fingerprint,
            items=metadata_items,
        ),
    )

    InstancesClient().set_metadata(request).result()
