import csv
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient


def get_vm_data(subscription_id):
    """Collect all VM metadata in one subscription."""
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    vm_list = []

    for vm in compute_client.virtual_machines.list_all():
        vm_id = vm.id
        vm_name = vm.name
        location = vm.location
        resource_group = vm_id.split("/")[4]

        # Get instance view (power state + status)
        instance_view = compute_client.virtual_machines.instance_view(
            resource_group_name=resource_group,
            vm_name=vm_name
        )

        power_state = None
        for status in instance_view.statuses:
            if status.code.startswith("PowerState"):
                power_state = status.code.split("/")[-1]

        # Get NIC info
        nics = vm.network_profile.network_interfaces
        private_ip = ""
        public_ip = ""

        if nics:
            nic_id = nics[0].id
            nic_name = nic_id.split("/")[-1]

            nic = network_client.network_interfaces.get(resource_group, nic_name)

            if nic.ip_configurations:
                ip_config = nic.ip_configurations[0]

                private_ip = ip_config.private_ip_address

                # Public IP
                if ip_config.public_ip_address:
                    public_ip_id = ip_config.public_ip_address.id
                    public_ip_name = public_ip_id.split("/")[-1]

                    public_ip_obj = network_client.public_ip_addresses.get(
                        resource_group,
                        public_ip_name
                    )
                    public_ip = public_ip_obj.ip_address

        # OS info
        os_type = vm.storage_profile.os_disk.os_type
        version = vm.storage_profile.image_reference.offer

        vm_row = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "vm_name": vm_name,
            "location": location,
            "power_state": power_state,
            "os_type": os_type,
            "version" : version,
            "private_ip": private_ip,
            "public_ip": public_ip,
            "vm_size": vm.hardware_profile.vm_size,
            "tags": str(vm.tags),
        }

        vm_list.append(vm_row)

    return vm_list


def main():
    credential = DefaultAzureCredential()
    subs_client = SubscriptionClient(credential)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    csv_filename = f"azure_vm_inventory_{timestamp}.csv"

    fieldnames = [
        "subscription_id", "resource_group", "vm_name", "location",
        "power_state", "os_type", "version","private_ip", "public_ip",
        "vm_size", "tags"
    ]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Collecting Azure VM data...")

        for sub in subs_client.subscriptions.list():
            sub_id = sub.subscription_id
            print(f"Processing subscription: {sub_id}")

            vm_data = get_vm_data(sub_id)

            for row in vm_data:
                writer.writerow(row)

        print(f"\n✔ Completed. CSV file saved as: {csv_filename}")


if __name__ == "__main__":
    main()
