# Setup Guide - Supply Chain Analytics

Complete setup instructions for the project.

## Prerequisites

- Python 3.12+
- Azure CLI installed and configured
- Azure subscription with permissions to create resources
- Git (for version control)

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd az-supply-chain-pipeline
```

### 2. Setup Python Environment

**Single virtual environment for entire project** (Best Practice)

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 3. Azure Login

```bash
az login
```

### 4. Create Azure Resources

```bash
cd infrastructure/scripts
python create_azure_resources.py "YourSQLPassword123!"
```

This creates:
- Resource Group
- Storage Account (Blob)
- Data Lake Gen2
- SQL Server & Database
- Data Factory

All credentials saved to `infrastructure/.env`

### 5. Generate Master Data

```bash
cd data_generation/master_data
python generate_master_data.py
```

Generates TSV compressed files:
- products_master.tsv.gz
- suppliers_master.tsv.gz
- warehouses_master.tsv.gz
- demand_demographics.tsv.gz

### 6. Upload Master Data

```bash
cd infrastructure/scripts
python upload_master_data.py
```

## Project Structure

```
az-supply-chain-pipeline/
├── venv/                          # Single virtual environment (DO NOT COMMIT)
├── requirements.txt               # All project dependencies
├── data_generation/
│   ├── master_data/
│   │   └── generate_master_data.py
│   ├── output/master_data/        # Generated files
│   └── transactional/
├── infrastructure/
│   ├── scripts/
│   │   ├── create_azure_resources.py
│   │   └── upload_master_data.py
│   └── .env                       # Azure credentials (DO NOT COMMIT)
├── README.md
└── SETUP.md                       # This file
```

## Dependencies

All dependencies in single `requirements.txt`:

**Data Generation:**
- pandas, numpy
- python-dateutil

**Transactional API:**
- fastapi, uvicorn
- pydantic

**Azure Infrastructure:**
- azure-storage-blob
- azure-mgmt-* (resource, storage, sql, datafactory)
- azure-identity
- tqdm

## Development Workflow

### Generate Data

```bash
# Activate venv
source venv/bin/activate

# Generate master data
python data_generation/master_data/generate_master_data.py

# Generate transactional data (TODO)
python data_generation/transactional/generate_transactional_data.py
```

### Infrastructure Management

```bash
# Create all resources
python infrastructure/scripts/create_azure_resources.py "Password123!"

# Upload master data
python infrastructure/scripts/upload_master_data.py

# Delete all resources
az group delete --name sca-rg-dev --yes
```

### API Development (TODO)

```bash
# Run transactional API
cd data_generation/transactional
uvicorn supply_chain_api:app --reload
```

## Environment Variables

All credentials in `infrastructure/.env`:

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

**Important:** `.env` file is gitignored - DO NOT COMMIT

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate
```

## Troubleshooting

### Virtual environment not activating

```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Module not found errors

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Azure authentication errors

```bash
# Login to Azure
az login

# Verify subscription
az account show
```

### Permission errors on Azure resources

Check that you have:
- Contributor role on subscription
- Storage Blob Data Contributor role
- SQL DB Contributor role

## Best Practices

1. **Single venv**: One virtual environment for entire project
2. **Requirements.txt**: Single requirements file in root
3. **Git ignore**: Never commit `.env`, `venv/`, or `__pycache__/`
4. **Credentials**: Always use environment variables
5. **Documentation**: Keep README and SETUP.md updated

## Next Steps

After setup:

1. Upload master data to Azure Blob Storage
2. Generate transactional data
3. Implement FastAPI for transactional endpoint
4. Create Azure Data Factory pipelines
5. Implement data transformations
6. Load data to SQL Database
7. Build Power BI dashboards

## Cost Management

- Development resources cost ~$8-12/month
- Delete resources when not in use to save costs
- Use Azure Cost Management for monitoring
