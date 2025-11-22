"""
Create Azure Resources using Python SDK
Direct, simple, works.
"""

import os
import sys
import time
from pathlib import Path
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient

from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.datafactory import DataFactoryManagementClient
import getpass


def load_env():
    """Load subscription ID from .env file"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith('AZURE_SUBSCRIPTION_ID'):
                    return line.split('=')[1].strip().strip('"').strip("'")
                elif line.startswith('SUBSCRIPTION_ID'):
                    value = line.split('=')[1].strip().strip('"').strip("'")
                    # Extract just the GUID if it's in /subscriptions/GUID format
                    if '/subscriptions/' in value:
                        return value.split('/subscriptions/')[-1]
                    return value
    return None

def main():
    print("Creating Azure Resources - Supply Chain Analytics")
    print("=" * 70)

    # Get credentials
    credential = AzureCliCredential()

    # Try to load subscription ID from .env
    subscription_id = load_env()
    if not subscription_id:
        subscription_id = input("Enter subscription ID: ").strip()
    else:
        print(f"\nUsing subscription ID from .env: {subscription_id[:8]}...")

    # Parameters
    location = "westus2"  # Changed from eastus due to SQL provisioning restrictions
    rg_name = "sca-rg-dev"

    # SQL password - from env var, arg, or prompt
    sql_password = os.environ.get('SQL_ADMIN_PASSWORD')
    if not sql_password and len(sys.argv) > 1:
        sql_password = sys.argv[1]
    if not sql_password:
        try:
            sql_password = getpass.getpass(
                "SQL Server password (min 8 chars, uppercase, lowercase, number): "
            )
        except (EOFError, KeyboardInterrupt):
            print("\nError: SQL password required. Provide via:")
            print("  - Environment variable: SQL_ADMIN_PASSWORD")
            print("  - Command line: python create_azure_resources.py <password>")
            sys.exit(1)

    # Clients
    resource_client = ResourceManagementClient(credential, subscription_id)
    storage_client = StorageManagementClient(credential, subscription_id)
    sql_client = SqlManagementClient(credential, subscription_id)
    adf_client = DataFactoryManagementClient(credential, subscription_id)

    # 1. Resource Group
    print(f"\n1. Creating Resource Group: {rg_name}")
    resource_client.resource_groups.create_or_update(rg_name, {"location": location})
    print("   Done")

    # 2. Storage Account (Blob)
    storage_name = f"scasa{os.urandom(4).hex()}"[:24]
    print(f"\n2. Creating Storage Account: {storage_name}")
    storage_client.storage_accounts.begin_create(
        rg_name,
        storage_name,
        {
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2",
            "location": location,
            "properties": {"supportsHttpsTrafficOnly": True}
        }
    ).result()
    time.sleep(5)  # Wait for storage account to be fully ready

    # Create container
    storage_client.blob_containers.create(rg_name, storage_name, "supply-chain-master-data", {})
    print("   Done")

    # 3. Data Lake
    dl_name = f"scadl{os.urandom(4).hex()}"[:24]
    print(f"\n3. Creating Data Lake: {dl_name}")
    storage_client.storage_accounts.begin_create(
        rg_name,
        dl_name,
        {
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2",
            "location": location,
            "properties": {
                "isHnsEnabled": True,
                "supportsHttpsTrafficOnly": True
            }
        }
    ).result()
    time.sleep(5)  # Wait for data lake to be fully ready

    for container in ["raw", "processed", "output"]:
        storage_client.blob_containers.create(rg_name, dl_name, container, {})
    print("   Done")

    # 4. SQL Server
    sql_server_name = f"sca-sql-{os.urandom(4).hex()}"
    print(f"\n4. Creating SQL Server: {sql_server_name}")
    sql_client.servers.begin_create_or_update(
        rg_name,
        sql_server_name,
        {
            "location": location,
            "administrator_login": "sqladmin",
            "administrator_login_password": sql_password,
            "version": "12.0"
        }
    ).result()

    # Firewall
    sql_client.firewall_rules.create_or_update(
        rg_name, sql_server_name, "AllowAzure",
        {"start_ip_address": "0.0.0.0", "end_ip_address": "0.0.0.0"}
    )
    sql_client.firewall_rules.create_or_update(
        rg_name, sql_server_name, "AllowAll",
        {"start_ip_address": "0.0.0.0", "end_ip_address": "255.255.255.255"}
    )
    print("   Done")

    # 5. SQL Database
    db_name = "sca-dw"
    print(f"\n5. Creating SQL Database: {db_name}")
    sql_client.databases.begin_create_or_update(
        rg_name,
        sql_server_name,
        db_name,
        {
            "location": location,
            "sku": {"name": "Basic", "tier": "Basic", "capacity": 5}
        }
    ).result()
    print("   Done")

    # 6. Data Factory
    adf_name = f"sca-adf-{os.urandom(4).hex()}"
    print(f"\n6. Creating Data Factory: {adf_name}")
    adf_client.factories.create_or_update(
        rg_name,
        adf_name,
        {"location": location, "identity": {"type": "SystemAssigned"}}
    )
    print("   Done")

    # Get connection strings
    print("\n" + "=" * 70)
    print("RESOURCES CREATED SUCCESSFULLY")
    print("=" * 70)

    keys = storage_client.storage_accounts.list_keys(rg_name, storage_name)
    storage_key = keys.keys[0].value
    storage_conn = f"DefaultEndpointsProtocol=https;AccountName={storage_name};AccountKey={storage_key};EndpointSuffix=core.windows.net"

    dl_keys = storage_client.storage_accounts.list_keys(rg_name, dl_name)
    dl_key = dl_keys.keys[0].value
    dl_conn = f"DefaultEndpointsProtocol=https;AccountName={dl_name};AccountKey={dl_key};EndpointSuffix=core.windows.net"

    # Save config
    config_file = "../config/azure_resources_python.txt"
    with open(config_file, "w") as f:
        f.write(f"Resource Group: {rg_name}\n")
        f.write(f"Storage Account: {storage_name}\n")
        f.write(f"Storage Connection: {storage_conn}\n\n")
        f.write(f"Data Lake: {dl_name}\n")
        f.write(f"Data Lake Connection: {dl_conn}\n\n")
        f.write(f"SQL Server: {sql_server_name}.database.windows.net\n")
        f.write(f"SQL Database: {db_name}\n")
        f.write(f"SQL User: sqladmin\n\n")
        f.write(f"Data Factory: {adf_name}\n")

    print(f"\nConfiguration saved to: {config_file}")
    print("\nUpdate infrastructure/config/azure_config.json with these values")

if __name__ == "__main__":
    main()
