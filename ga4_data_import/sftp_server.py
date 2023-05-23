#@title Some code here
import json
import os
import subprocess
from googleapiclient import discovery

DEBUG = False

def create_instance(
    INSTANCE_NAME,
    GCP_PROJECT_ID,
    REGION,
    ZONE,
    SFTP_USERNAME,
    BUCKET_NAME,
):
    """
    Returns:
        dict, https://cloud.google.com/compute/docs/reference/rest/v1/instances#resource:-instance
    """
    statis_ip_create_cmd = f"""
        gcloud compute addresses create {INSTANCE_NAME}-static \
            --project={GCP_PROJECT_ID} \
            --network-tier=STANDARD \
            --region={REGION} \
            --format='value(address)'
    """

    #static_ip = subprocess.check_output(statis_ip_create_cmd, shell=True).decode().strip()
    static_ip = "35.208.180.229"

    startup_script = f"""
#!/bin/bash

SFTP_USERNAME={SFTP_USERNAME}
BUCKET_NAME={BUCKET_NAME}

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
adduser $SFTP_USERNAME
mkdir /home/$SFTP_USERNAME
chown root:root /home/sftp_user
sed -i "s/^Subsystem\tsftp.*/Subsystem\tsftp internal-sftp/" /etc/ssh/sshd_config
tee -a /etc/ssh/sshd_config << EOM
Match User $SFTP_USERNAME
\tForceCommand internal-sftp -d /sftp
\tChrootDirectory /home/%u
\tAllowTcpForwarding no
\tX11Forwarding no
\tPasswordAuthentication no
\tAuthenticationMethods publickey
EOM
systemctl restart ssh

# Mount bucket
sudo -u $SFTP_USERNAME mkdir /home/$SFTP_USERNAME/sftp
sudo -u $SFTP_USERNAME gcsfuse $BUCKET_NAME /home/$SFTP_USERNAME/sftp"""
    with open('startup.sh', 'w') as file:
        file.write(startup_script)

    instance_create_cmd = f"""
    gcloud compute instances create {INSTANCE_NAME} \
        --project={GCP_PROJECT_ID} \
        --zone={ZONE} \
        --machine-type=f1-micro \
        --network-interface=address={static_ip},network-tier=STANDARD,subnet=default \
        --maintenance-policy=MIGRATE \
        --provisioning-model=STANDARD \
        --service-account={PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
        --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
        --tags=default-allow-ssh \
        --create-disk=auto-delete=yes,boot=yes,image=projects/debian-cloud/global/images/debian-11-bullseye-v20230509,mode=rw,size=10,type=projects/max-ostapenko/zones/us-central1-a/diskTypes/pd-balanced \
        --no-shielded-secure-boot \
        --shielded-vtpm \
        --shielded-integrity-monitoring \
        --labels=ec-src=vm_add-gcloud \
        --reservation-affinity=any \
        --metadata-from-file=startup-script=startup.sh \
        --format=json
    """
    instance_info = json.loads(subprocess.check_output(instance_create_cmd, shell=True))[0]

    return instance_info


def add_shh_pub_key(key):
    """
    Args:
        key: SSH public key value

    """
    # Get the existing SSH keys from current instance metadata
    instance_describe_cmd = f"""
    gcloud compute instances describe {INSTANCE_NAME} \
        --project={GCP_PROJECT_ID} \
        --zone={ZONE} \
        --format='json(metadata)'
    """
    metadata = json.loads(subprocess.check_output(instance_describe_cmd, shell=True))

    existing_keys = ""
    for metadata_item in metadata.get("metadata",{}).get("items",{}):
        if metadata_item.get("key","") == "ssh-keys":
            existing_keys = metadata_item.get("value","")
            break

    new_key = f"{SFTP_USERNAME}:{key}".strip()
    need_append = True
    for key in existing_keys.splitlines():
        key = key.strip()
        if new_key == key:
            need_append = False
            break

    # Append the new public key to the VM SSH keys
    if DEBUG:
        print(f"""Existing keys:
{existing_keys}
New key:
{new_key}
    """)

    # Update the instance metadata with the new SSH keys
    if need_append:
        keys_file = "keys.txt"
        with open(keys_file, "w") as file:
            if existing_keys:
                file.write(f"{existing_keys}\n{new_key}")
            else:
                file.write(f"{new_key}")
        !gcloud compute instances add-metadata {INSTANCE_NAME} --project={GCP_PROJECT_ID} --zone={ZONE} --metadata-from-file=ssh-keys={keys_file}
        !rm keys.txt
