# Infrastructure - Azure Resources

All Azure infrastructure for the Supply Chain Analytics project.

## Resources Created

### Resource Group
- **Name**: `sca-rg-dev`
- **Location**: `westus2`
- **Purpose**: Container for all project resources

### Storage Account (Blob Storage)
- **Name**: `scasae8c2b276`
- **Type**: StorageV2, Standard_LRS
- **Container**: `supply-chain-master-data`
- **Purpose**: Store master data files (products, suppliers, warehouses)

### Data Lake Storage Gen2
- **Name**: `scadlac398199`
- **Type**: StorageV2 with hierarchical namespace enabled
- **Containers**:
  - `raw` - Raw ingested data
  - `processed` - Transformed data
  - `output` - Final output for loading
- **Purpose**: ETL pipeline data processing

### Azure SQL Server
- **Server**: `sca-sql-c7f006ea.database.windows.net`
- **Database**: `sca-dw`
- **Admin User**: `sqladmin`
- **Firewall**: Configured to allow Azure services and all IPs (development only)
- **Purpose**: Data warehouse for analytics

### Azure Data Factory
- **Name**: `sca-adf-fef56bb2`
- **Identity**: System-assigned managed identity
- **Purpose**: Orchestrate ETL/ELT pipelines

## Directory Structure

```
infrastructure/
├── scripts/
│   ├── create_azure_resources.py  # Azure SDK resource creation
│   └── upload_master_data.py      # Upload data to Blob Storage
├── .env                           # Azure credentials (DO NOT COMMIT)
├── requirements.txt               # Azure SDK dependencies
└── README.md                      # This file
```

## Prerequisites

### Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Required packages:
- `azure-storage-blob`: Blob Storage operations
- `azure-identity`: Authentication
- `azure-mgmt-resource`: Resource Group management
- `azure-mgmt-storage`: Storage Account management
- `azure-mgmt-sql`: SQL Server management
- `azure-mgmt-datafactory`: Data Factory management
- `tqdm`: Progress bars

## Deployment

### Create Resources

```bash
cd infrastructure/scripts
source ../../venv/bin/activate
python create_azure_resources.py "YourSQLPassword123!"
```

The script:
1. Reads subscription ID from `infrastructure/.env`
2. Creates Resource Group in westus2
3. Creates Storage Account with container
4. Creates Data Lake Gen2 with containers
5. Creates SQL Server and Database
6. Creates Data Factory with managed identity
7. Saves all credentials to `infrastructure/.env`

### Upload Master Data

```bash
cd infrastructure/scripts
source ../../venv/bin/activate
python upload_master_data.py
```

Uploads all `.tsv.gz` files from `data/master_data/` to Blob Storage.

Options:
- `--dry-run` - Test without uploading
- `--verbose` - Show detailed progress

## Configuration

All credentials stored in `infrastructure/.env`:

```env
# Azure Subscription
SUBSCRIPTION_ID=/subscriptions/...

# Resource Group
RESOURCE_GROUP=sca-rg-dev
LOCATION_ID=westus2

# Storage Account
STORAGE_ACCOUNT_NAME=scasae8c2b276
STORAGE_CONNECTION_STRING=...

# Data Lake
DATA_LAKE_NAME=scadlac398199
DATA_LAKE_CONNECTION_STRING=...

# SQL Server
SQL_SERVER_FQDN=sca-sql-c7f006ea.database.windows.net
SQL_DATABASE_NAME=sca-dw
SQL_ADMIN_USERNAME=sqladmin
SQL_ADMIN_PASSWORD=...

# Data Factory
DATA_FACTORY_NAME=sca-adf-fef56bb2
```

## Scripts

### create_azure_resources.py

Creates all Azure resources using Azure Python SDK.

Features:
- Automatic subscription ID detection from `.env`
- SQL password via environment variable, command-line, or prompt
- Error handling and retry logic
- Connection string generation
- Automatic credential saving

### upload_master_data.py

Uploads master data files to Azure Blob Storage.

Features:
- Automatic connection string from `.env`
- Progress bar for uploads
- Dry-run mode for testing
- Batch upload with error handling
- Upload verification

## Clean Up

To delete all resources:

```bash
az group delete --name sca-rg-dev --yes
```

**Warning**: This deletes all resources and data permanently.

## Troubleshooting

### Resource creation failed

Check Azure quotas and region availability. If SQL Server provisioning fails, try a different region.

### Upload errors

Verify connection string in `.env` file and ensure Storage Account exists.

### Authentication errors

Run `az login` to authenticate with Azure CLI.

## Security Notes

- `.env` file contains sensitive credentials - **DO NOT COMMIT**
- SQL Server firewall configured for development (allows all IPs)
- For production: restrict firewall to specific IPs
- For production: use Azure Key Vault for secrets
- For production: use managed identities instead of connection strings

## Cost Optimization

Current configuration uses minimal tiers:

- Storage: Standard_LRS (lowest cost)
- SQL Database: Basic tier (5 DTU, 2GB)
- Data Factory: Pay-per-use

Estimated cost: ~$8-12/month

To reduce costs further:

- Delete resources when not in use
- Use serverless SQL database tier
- Schedule auto-shutdown for development resources
