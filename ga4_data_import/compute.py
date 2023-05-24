# @title Some code here
from google.cloud import compute_v1
from ga4_data_import.common import get_region_from_zone, wait_for_operation


def create_static_address(instance_name, project_id, zone):
    """
    Create a static address with the provided name, project id, and region.
    Args:
        instance_name: The name of the instance.
        project_id: The project id.
        zone: The zone to create the static address in.
    Returns:
        str, The static address.
    """
    compute_client = compute_v1.AddressesClient()
    region = get_region_from_zone(zone)

    address_name = f"{instance_name}-static"
    # Prepare the request body
    address_request = compute_v1.InsertAddressRequest(
        project=project_id,
        region=region,
        address_resource=compute_v1.Address(name=address_name, network_tier="STANDARD"),
    )

    # Create the static address
    operation = compute_client.insert(address_request)
    wait_for_operation(operation=operation, project_id=project_id)

    address_request = compute_v1.GetAddressRequest(
        project=project_id, region=region, address=address_name
    )
    address_response = compute_client.get(address_request)

    return address_response.address


def create_instance(instance_name, project_id, zone, sftp_username, bucket_name):
    """
    Create a Compute Engine instance with the provided name, project id, zone, and bucket name.
    Args:
        instance_name: The name of the instance.
        project_id: The project id.
        zone: The zone to create the instance in.
        sftp_username: The username to create on the instance.
        bucket_name: The name of the bucket to mount on the instance.
    Returns:
        str, The static address.
    """
    region = get_region_from_zone(zone)
    static_address = create_static_address(instance_name, project_id, zone)

    client = compute_v1.InstancesClient()

    # Create the instance request
    network_interface = compute_v1.NetworkInterface(
        name=f"{instance_name}-nic0",
        access_configs=[
            compute_v1.AccessConfig(
                name="external-nat",
                type_="ONE_TO_ONE_NAT",
                nat_i_p=static_address,
                network_tier="STANDARD",
            )
        ],
    )
    scopes = [
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/logging.write",
        "https://www.googleapis.com/auth/monitoring.write",
        "https://www.googleapis.com/auth/servicecontrol",
        "https://www.googleapis.com/auth/service.management.readonly",
        "https://www.googleapis.com/auth/trace.append",
    ]
    disk = (
        "auto-delete=yes,boot=yes,"
        + "image=projects/debian-cloud/global/images/debian-11-bullseye-v20230509,"
        + "mode=rw,size=10,"
        + f"type=projects/{project_id}/zones/{zone}/diskTypes/pd-balanced"
    )
    request = {
        "project": project_id,
        "zone": zone,
        "instance_resource": {
            "name": instance_name,
            "machine_type": f"projects/{project_id}/zones/{zone}/machineTypes/f1-micro",
            "network_interfaces": [network_interface],
            "service_accounts": [
                {
                    "email": f"{project_id}-compute@developer.gserviceaccount.com",
                    "scopes": scopes,
                }
            ],
            "tags": {"items": ["default-allow-ssh"]},
            "disks": [
                {
                    "initialize_params": {"source_image": disk},
                    "boot": True,
                    "auto_delete": True,
                }
            ],
            "shielded_instance_config": {
                "enable_secure_boot": False,
                "enable_vtpm": True,
                "enable_integrity_monitoring": True,
            },
            "scheduling": {
                "on_host_maintenance": "MIGRATE",
                "automatic_restart": True,
                "preemptible": False,
            },
        },
    }

    metadata = [
        (
            "startup-script",
            f"""#!/bin/bash

sftp_username={sftp_username}
bucket_name={bucket_name}

# Install SFTP server
apt-get update -y
apt-get install -y openssh-server

# Install gcloud
# https://cloud.google.com/sdk/docs/install#installation_instructions
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | tee /usr/share/keyrings/cloud.google.gpg
apt-get update -y
apt-get install google-cloud-sdk -y

# Install gcsfuse
# https://cloud.google.com/storage/docs/gcsfuse-quickstart-mount-bucket#install
export GCSFUSE_REPO=gcsfuse-$(lsb_release -c -s)
echo "deb https://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update -y
sudo apt-get install -y fuse gcsfuse
rm -rf /var/lib/apt/lists/*

# Create user
adduser $sftp_username
mkdir /home/$sftp_username
chown root:root /home/sftp_user
sed -i "s/^Subsystem\tsftp.*/Subsystem\tsftp internal-sftp/" /etc/ssh/sshd_config
tee -a /etc/ssh/sshd_config << EOM
Match User $sftp_username
\tForceCommand internal-sftp -d /sftp
\tChrootDirectory /home/%u
\tAllowTcpForwarding no
\tX11Forwarding no
\tPasswordAuthentication no
\tAuthenticationMethods publickey
EOM
systemctl restart ssh

# Mount bucket
sudo -u $sftp_username mkdir /home/$sftp_username/sftp
sudo -u $sftp_username gcsfuse $bucket_name /home/$sftp_username/sftp""",
        )
    ]

    # Create the instance
    operation = client.insert(request=request, metadata=metadata)
    # Wait for the operation to complete
    wait_for_operation(operation=operation, project_id=project_id)

    return static_address


def add_shh_pub_key(project_id, zone, instance_name, sftp_username, key):
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

    client = compute_v1.InstancesClient()

    instance_response = client.get(
        project=project_id, zone=zone, instance=instance_name
    )
    metadata = instance_response.get("metadata")
    instance_path = instance_response.get("selfLink")
    ssh_keys = metadata.get("ssh-keys")

    # metadata = json.loads(subprocess.check_output(instance_describe_cmd, shell=True))

    new_key = f"{sftp_username}:{key}".strip()
    existing_keys = []
    need_append = True
    if ssh_keys:
        existing_keys = ssh_keys.split("\n")
        for key in existing_keys:
            # Process each SSH key as needed
            print(key)
            existing_keys.append(key.strip())
            if new_key == key:
                need_append = False
                break
    # else:
    # print('No SSH keys found in instance metadata.')

    # Append the new public key to the VM SSH keys
    if True:
        print(
            f"""Existing keys:
{existing_keys}
New key:
{new_key}
    """
        )

    # Update the instance metadata with the new SSH keys
    if need_append:
        metadata = {"ssh-keys": "\n".join(["\n".join(existing_keys), new_key])}

        request = compute_v1.AddMetadataItemsRequest(
            instance=instance_path, metadata=metadata
        )

        client.add_metadata(request)
