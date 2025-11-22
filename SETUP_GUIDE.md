# Setup Guide - Step by Step

This guide will walk you through setting up and using the professional Python upload script.

## Step 1: Generate Master Data (TSV Compressed)

```bash
cd data_generation
./run_all.sh setup    # Install dependencies (first time only)
./run_all.sh master   # Generate master data as .tsv.gz files
```

**Expected output:**
```
data_generation/output/master_data/
├── products/products_master.tsv.gz
├── suppliers/suppliers_master.tsv.gz
├── warehouses/warehouses_master.tsv.gz
└── demographics/demand_demographics.tsv.gz
```

## Step 2: Install Infrastructure Dependencies

```bash
cd ../infrastructure
pip install -r requirements.txt
```

## Step 3: Get Your Azure Connection String

### Option A: Using Azure Portal (Recommended)

1. Go to https://portal.azure.com
2. Navigate to your **Storage Account**
3. In the left menu, click **Access keys**
4. Click **Show** next to "Connection string" for key1
5. Click the **Copy** button
6. Save it temporarily in a text file

### Option B: Using Azure CLI

```bash
az storage account show-connection-string \
  --name YOUR_STORAGE_ACCOUNT_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --output tsv
```

## Step 4: Configure Credentials

```bash
cd config/
cp azure_config.template.json azure_config.json
nano azure_config.json  # or use your preferred editor
```

Replace these values:

```json
{
  "storage_account": {
    "name": "YOUR_ACTUAL_STORAGE_ACCOUNT_NAME",
    "connection_string": "PASTE_YOUR_CONNECTION_STRING_HERE",
    "container_name": "supply-chain-master-data"
  },
  ...
}
```

**Save and close** the file.

## Step 5: Test Upload (Dry Run)

```bash
cd ../scripts/
python upload_master_data.py --dry-run
```

**What this does:**
- Connects to Azure (verifies credentials)
- Lists files to upload
- Simulates upload without actually uploading
- Shows what would happen

**Expected output:**
```
Connecting to Azure Blob Storage...
Successfully connected to Storage Account
   Account type: Standard_LRS
Container 'supply-chain-master-data' exists

UPLOADING MASTER DATA TO AZURE BLOB STORAGE

DRY-RUN MODE: Files will not be actually uploaded

Files found: 4
Total size: 45.32 KB

Starting upload...
  [DRY-RUN] products/products_master.tsv.gz (12.45 KB)
  [DRY-RUN] suppliers/suppliers_master.tsv.gz (8.23 KB)
  [DRY-RUN] warehouses/warehouses_master.tsv.gz (5.12 KB)
  [DRY-RUN] demographics/demand_demographics.tsv.gz (19.52 KB)

Uploading: 100%|████████████████| 4/4

UPLOAD SUMMARY
Mode:              DRY-RUN (simulation)
Total files:       4
Uploaded:          4
Skipped:           0
Failed:            0
```

## Step 6: Real Upload

If dry run was successful:

```bash
python upload_master_data.py
```

**Expected output:**
```
Connecting to Azure Blob Storage...
Successfully connected to Storage Account

UPLOADING MASTER DATA TO AZURE BLOB STORAGE

Files found: 4
Total size: 45.32 KB

Starting upload...
  OK: products/products_master.tsv.gz (12.45 KB)
  OK: suppliers/suppliers_master.tsv.gz (8.23 KB)
  OK: warehouses/warehouses_master.tsv.gz (5.12 KB)
  OK: demographics/demand_demographics.tsv.gz (19.52 KB)

Uploading: 100%|████████████████| 4/4

UPLOAD SUMMARY
Mode:              REAL
Total files:       4
Uploaded:          4
Skipped:           0
Failed:            0
Total uploaded:    45.32 KB

Upload completed successfully!

Verify in Azure Portal:
   Storage Account: YOUR_STORAGE_ACCOUNT_NAME
   Container: supply-chain-master-data
```

## Step 7: Verify in Azure Portal

1. Go to **Azure Portal**
2. Navigate to your **Storage Account**
3. Click **Storage Browser** (left menu)
4. Click **Blob containers**
5. Open **supply-chain-master-data**
6. You should see:
   ```
   products/
    products_master.tsv.gz
   suppliers/
      suppliers_master.tsv.gz
   warehouses/
      warehouses_master.tsv.gz
   demographics/
      demand_demographics.tsv.gz
   ```

## Common Issues and Solutions

### Issue: "Configuration file not found"

**Cause:** You didn't create `azure_config.json`

**Solution:**
```bash
cd infrastructure/config
cp azure_config.template.json azure_config.json
# Edit the file with your credentials
```

### Issue: "Error connecting to Azure"

**Cause:** Wrong connection string or insufficient permissions

**Solutions:**
1. Verify connection string is correct (copy again from Portal)
2. Ensure no extra spaces or quotes
3. Check you have "Storage Blob Data Contributor" role

### Issue: "No .tsv.gz files found"

**Cause:** Master data not generated yet

**Solution:**
```bash
cd data_generation
./run_all.sh master
```

### Issue: "Files already exist, all skipped"

**Cause:** Files were already uploaded

**Solutions:**
- This is normal behavior (prevents duplicates)
- To force re-upload: `python upload_master_data.py --overwrite`

## Check Logs

Every upload creates a log file in `infrastructure/scripts/`:

```bash
cat upload_20241120_143052.log
```

## Next Steps

After successfully uploading master data:

1. **Start transactional data API:**
   ```bash
   cd data_generation
   ./run_all.sh api
   ```

2. **Configure Azure Data Factory:**
   - Create HTTP Linked Service (pointing to your API)
   - Create Blob Storage Linked Service (already has your data)
   - Create Data Lake Linked Service
   - Create Copy Activities

3. **Implement transformations**

## Tips for Your Portfolio

When showcasing this in interviews/LinkedIn:

**What you can say:**

> "I developed a professional Python script using Azure SDK to upload master data to Blob Storage. The script includes error handling, progress tracking, dry-run capability, and comprehensive logging. It demonstrates production-ready code practices and Azure cloud proficiency."

**Key highlights:**
- Professional Python code
- Azure SDK expertise
- Error handling and validation
- Logging and monitoring
- Production best practices
- Well-documented

---

**Questions?** Check [infrastructure/README.md](infrastructure/README.md) for detailed documentation.
