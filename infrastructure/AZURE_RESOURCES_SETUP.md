# Azure Resources Setup Guide

Complete guide to create all necessary Azure resources for the Supply Chain Analytics project.

## Overview

Resources needed:
1. Resource Group
2. Storage Account (Blob Storage for master data)
3. Data Lake Storage Gen2 (for raw/processed data)
4. Azure SQL Server
5. Azure SQL Database
6. Azure Data Factory

## Prerequisites

- Azure subscription
- Azure CLI installed (or use Azure Portal)
- Contributor or Owner role on subscription

## Option 1: Using Azure Portal (Recommended for Beginners)

### Step 1: Create Resource Group

1. Go to Azure Portal: https://portal.azure.com
2. Click **Resource groups** (left menu or search)
3. Click **+ Create**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `supplychain-reporting-rg`
   - **Region**: `East US` (or your preferred region)
5. Click **Review + create** → **Create**

**Save this info:**
```
Resource Group Name: supplychain-reporting-rg
Region: East US
```

---

### Step 2: Create Storage Account (Blob Storage)

This will store master data (products, suppliers, warehouses, demographics).

1. In Azure Portal, click **Storage accounts** → **+ Create**
2. Fill in:
   - **Resource group**: `supplychain-reporting-rg`
   - **Storage account name**: `supplychainsa` (must be globally unique, try: `supplychainsa[yourname]`)
   - **Region**: `East US` (same as resource group)
   - **Performance**: `Standard`
   - **Redundancy**: `Locally-redundant storage (LRS)`
3. Click **Review** → **Create**
4. Wait for deployment to complete

**After creation:**
1. Go to the storage account
2. Click **Access keys** (left menu)
3. Click **Show** next to Connection string for key1
4. Copy and save it

**Save this info:**
```
Storage Account Name: supplychainsa[yourname]
Connection String: DefaultEndpointsProtocol=https;AccountName=...
Purpose: Master data (Blob Storage)
```

**Create container:**
1. In the storage account, click **Containers** (left menu)
2. Click **+ Container**
3. Name: `supply-chain-master-data`
4. Click **Create**

---

### Step 3: Create Data Lake Storage Gen2

This will store raw and processed transactional data.

1. In Azure Portal, click **Storage accounts** → **+ Create**
2. Fill in:
   - **Resource group**: `supplychain-reporting-rg`
   - **Storage account name**: `supplychaindl` (must be unique, try: `supplychaindl[yourname]`)
   - **Region**: `East US`
   - **Performance**: `Standard`
   - **Redundancy**: `Locally-redundant storage (LRS)`
3. Click **Advanced** tab
4. Check **Enable hierarchical namespace** (this makes it Data Lake Gen2)
5. Click **Review** → **Create**

**After creation:**
1. Go to the storage account
2. Click **Access keys**
3. Copy connection string

**Save this info:**
```
Data Lake Name: supplychaindl[yourname]
Connection String: DefaultEndpointsProtocol=https;AccountName=...
Purpose: Raw and processed data (Data Lake Gen2)
```

**Create containers:**
1. In the storage account, click **Containers**
2. Create these containers:
   - `raw` (for raw data from API)
   - `processed` (for transformed data)
   - `output` (for final data to SQL)

---

### Step 4: Create Azure SQL Server

1. In Azure Portal, search for **SQL servers** → **+ Create**
2. Fill in:
   - **Resource group**: `supplychain-reporting-rg`
   - **Server name**: `supplychain-sql-server` (must be unique, try: `supplychain-sql-server-[yourname]`)
   - **Region**: `East US`
   - **Authentication method**: `Use SQL authentication`
   - **Server admin login**: `sqladmin`
   - **Password**: Create a strong password (save it!)
3. Click **Networking** tab
4. **Firewall rules**:
   - Check **Allow Azure services and resources to access this server**
   - Check **Add current client IP address** (so you can connect from your computer)
5. Click **Review + create** → **Create**

**Save this info:**
```
SQL Server Name: supplychain-sql-server-[yourname].database.windows.net
Admin Login: sqladmin
Admin Password: [YOUR_PASSWORD]
```

---

### Step 5: Create Azure SQL Database

1. In Azure Portal, search for **SQL databases** → **+ Create**
2. Fill in:
   - **Resource group**: `supplychain-reporting-rg`
   - **Database name**: `supplychain-dw`
   - **Server**: Select the SQL Server you just created
3. **Compute + storage**: Click **Configure database**
   - Select **Basic** (5 DTUs, 2GB) - cheapest option for learning
4. Click **Backup storage redundancy**: `Locally-redundant`
5. Click **Review + create** → **Create**

**After creation, get connection string:**
1. Go to the database
2. Click **Connection strings** (left menu)
3. Copy the **ADO.NET** connection string
4. Replace `{your_password}` with your actual password

**Save this info:**
```
Database Name: supplychain-dw
Server: supplychain-sql-server-[yourname].database.windows.net
Connection String: Server=tcp:supplychain-sql-server...
```

---

### Step 6: Create Azure Data Factory

1. In Azure Portal, search for **Data factories** → **+ Create**
2. Fill in:
   - **Resource group**: `supplychain-reporting-rg`
   - **Region**: `East US`
   - **Name**: `supplychain-adf` (must be unique, try: `supplychain-adf-[yourname]`)
   - **Version**: `V2`
3. **Git configuration**: Skip for now (click **Configure Git later**)
4. Click **Review + create** → **Create**

**Save this info:**
```
Data Factory Name: supplychain-adf-[yourname]
```

---

## Option 2: Using Azure CLI (Faster, Automated)

If you have Azure CLI installed:

```bash
# Login to Azure
az login

# Set variables (change these)
RG_NAME="supplychain-reporting-rg"
LOCATION="eastus"
SA_NAME="supplychainsa${USER}"  # Add your username for uniqueness
DL_NAME="supplychaindl${USER}"
SQL_SERVER="supplychain-sql-${USER}"
SQL_DB="supplychain-dw"
SQL_ADMIN="sqladmin"
SQL_PASSWORD="YourStrongPassword123!"  # Change this!
ADF_NAME="supplychain-adf-${USER}"

# 1. Create Resource Group
az group create --name $RG_NAME --location $LOCATION

# 2. Create Storage Account (Blob)
az storage account create \
  --name $SA_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --sku Standard_LRS

# Create container
az storage container create \
  --account-name $SA_NAME \
  --name supply-chain-master-data

# Get connection string
az storage account show-connection-string \
  --name $SA_NAME \
  --resource-group $RG_NAME

# 3. Create Data Lake Gen2
az storage account create \
  --name $DL_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --sku Standard_LRS \
  --enable-hierarchical-namespace true

# Create containers
az storage container create --account-name $DL_NAME --name raw
az storage container create --account-name $DL_NAME --name processed
az storage container create --account-name $DL_NAME --name output

# Get connection string
az storage account show-connection-string \
  --name $DL_NAME \
  --resource-group $RG_NAME

# 4. Create SQL Server
az sql server create \
  --name $SQL_SERVER \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --admin-user $SQL_ADMIN \
  --admin-password $SQL_PASSWORD

# Configure firewall
az sql server firewall-rule create \
  --resource-group $RG_NAME \
  --server $SQL_SERVER \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

az sql server firewall-rule create \
  --resource-group $RG_NAME \
  --server $SQL_SERVER \
  --name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP

# 5. Create SQL Database
az sql db create \
  --resource-group $RG_NAME \
  --server $SQL_SERVER \
  --name $SQL_DB \
  --service-objective Basic

# 6. Create Data Factory
az datafactory create \
  --resource-group $RG_NAME \
  --name $ADF_NAME \
  --location $LOCATION
```

---

## After Creating Resources

### Update your configuration file

Edit `infrastructure/config/azure_config.json`:

```json
{
  "storage_account": {
    "name": "supplychainsa[yourname]",
    "connection_string": "PASTE_YOUR_BLOB_STORAGE_CONNECTION_STRING",
    "container_name": "supply-chain-master-data"
  },
  "data_lake": {
    "name": "supplychaindl[yourname]",
    "connection_string": "PASTE_YOUR_DATA_LAKE_CONNECTION_STRING",
    "container_name": "raw"
  },
  "sql_database": {
    "server": "supplychain-sql-server-[yourname].database.windows.net",
    "database": "supplychain-dw",
    "username": "sqladmin",
    "password": "YOUR_SQL_PASSWORD",
    "connection_string": "Server=tcp:supplychain-sql-server...;Database=supplychain-dw;User ID=sqladmin;Password=...;Encrypt=true;TrustServerCertificate=false;"
  },
  "data_factory": {
    "name": "supplychain-adf-[yourname]",
    "resource_group": "supplychain-reporting-rg"
  }
}
```

---

## Cost Estimation

For learning/development with minimal data:

| Resource | Tier | Monthly Cost (USD) |
|----------|------|-------------------|
| Storage Account | Standard LRS | ~$0.02/GB (~$1/month) |
| Data Lake Gen2 | Standard LRS | ~$0.02/GB (~$1/month) |
| SQL Database | Basic (5 DTU) | ~$5/month |
| SQL Server | No charge | $0 |
| Data Factory | Pay per use | ~$1-5/month |
| **Total** | | **~$8-12/month** |

**Important:** Delete resources when not in use to avoid charges!

---

## Verify Resources

After creation, verify all resources exist:

```bash
az resource list --resource-group supplychain-reporting-rg --output table
```

You should see:
- 2 Storage accounts (Blob + Data Lake)
- 1 SQL Server
- 1 SQL Database
- 1 Data Factory

---

## Security Notes

1. **Never commit** connection strings to GitHub
2. **Use** `.env` or `azure_config.json` (already in .gitignore)
3. **Rotate** access keys regularly
4. **Restrict** SQL Server firewall rules to your IP only
5. **Use** Managed Identities in production

---

## Next Steps

After creating all resources:

1. ✅ Update `infrastructure/config/azure_config.json` with connection strings
2. ✅ Test upload: `python infrastructure/scripts/upload_master_data.py --dry-run`
3. ✅ Real upload: `python infrastructure/scripts/upload_master_data.py`
4. ✅ Configure Azure Data Factory pipelines
5. ✅ Create transformations

---

**Created:** 2024-11-20
**Version:** 1.0
