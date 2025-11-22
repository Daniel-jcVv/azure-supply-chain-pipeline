# Supply Chain Analytics - Azure Data Engineering Project

Portfolio project demonstrating end-to-end Azure data engineering pipeline for supply chain analytics.

Based on the COVID-19 Azure Data Factory tutorial, adapted to supply chain domain with synthetic data generation.

## Project Overview

This project implements a complete data engineering solution using Azure services to process and analyze supply chain data:

- **Data Sources**: Synthetic master data (products, suppliers, warehouses) and transactional data (shipments, purchase orders, inventory)
- **Storage**: Azure Blob Storage for master data, Azure Data Lake Gen2 for ETL processing
- **Processing**: Azure Data Factory orchestration, Databricks/HDInsight for transformations
- **Data Warehouse**: Azure SQL Database
- **Visualization**: Power BI dashboards

## Architecture

```
Master Data (Blob Storage)          Transactional API (FastAPI)
        |                                    |
        |                                    |
        v                                    v
    Azure Data Factory (Orchestration)
        |
        v
    Data Lake Gen2 (Raw -> Processed -> Output)
        |
        v
    Transformations (Databricks/HDInsight)
        |
        v
    Azure SQL Database (Data Warehouse)
        |
        v
    Power BI (Analytics & Dashboards)
```

## Azure Resources

All resources deployed in **westus2** region:

- **Resource Group**: `sca-rg-dev`
- **Storage Account**: `scasae8c2b276` (master data)
- **Data Lake Gen2**: `scadlac398199` (raw/processed/output)
- **SQL Server**: `sca-sql-c7f006ea.database.windows.net`
- **SQL Database**: `sca-dw`
- **Data Factory**: `sca-adf-fef56bb2`

All credentials and connection strings stored in `infrastructure/.env`

## Project Structure

```
az-supply-chain-pipeline/
├── data_generation/
│   ├── master_data/
│   │   └── generate_master_data.py    # Generate products, suppliers, warehouses
│   ├── transactional_data/
│   │   └── generate_transactions.py   # Generate shipments, POs, inventory
│   └── api/
│       └── main.py                    # FastAPI for transactional data
├── infrastructure/
│   ├── scripts/
│   │   ├── create_azure_resources.py  # Azure SDK resource creation
│   │   └── upload_master_data.py      # Upload data to Blob Storage
│   ├── .env                           # Azure credentials (DO NOT COMMIT)
│   └── requirements.txt               # Azure SDK dependencies
├── data/
│   └── master_data/                   # Generated TSV.GZ files
└── README.md
```

## Setup & Deployment

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r infrastructure/requirements.txt
```

### 2. Generate Master Data

```bash
cd data_generation/master_data
python generate_master_data.py
```

Generates TSV compressed files:
- `products.tsv.gz`
- `suppliers.tsv.gz`
- `warehouses.tsv.gz`
- `demographics.tsv.gz`

### 3. Create Azure Resources

```bash
cd infrastructure/scripts
python create_azure_resources.py "YourSQLPassword123!"
```

Creates all Azure resources and saves credentials to `infrastructure/.env`

### 4. Upload Master Data

```bash
cd infrastructure/scripts
python upload_master_data.py
```

Uploads all master data files to Azure Blob Storage.

## Data Sources Mapping

Original COVID-19 project mapped to Supply Chain domain:

| COVID-19 Source | Supply Chain Equivalent | Type |
|----------------|------------------------|------|
| ECDC COVID API | Transactional API (shipments, POs, inventory) | REST API |
| Eurostat Population | Master Data (products, suppliers, warehouses) | Blob Storage |

## Technologies Used

### Azure Services
- Azure Data Factory
- Azure Blob Storage
- Azure Data Lake Gen2
- Azure SQL Database
- Azure Databricks / HDInsight

### Development
- Python 3.12
- Azure SDK for Python
- Pandas
- FastAPI (for transactional API)
- Azure CLI

### Data Format
- TSV Compressed (.tsv.gz) for master data
- JSON for API responses

## Current Status

- [x] Project architecture defined
- [x] Master data generation (TSV compressed format)
- [x] Azure resources created via Python SDK
- [x] Storage accounts configured
- [x] SQL Database provisioned
- [x] Data Factory created
- [ ] Transactional data generation
- [ ] FastAPI implementation
- [ ] Master data upload to Blob Storage
- [ ] Data Factory pipelines
- [ ] Data transformations (Databricks/HDInsight)
- [ ] SQL Database schema & loading
- [ ] Power BI dashboards

## Next Steps

1. Upload master data to Azure Blob Storage
2. Generate transactional data (shipments, POs, inventory)
3. Implement FastAPI for transactional data endpoint
4. Create Azure Data Factory pipelines
5. Implement data transformations
6. Load data into SQL Database
7. Build Power BI dashboards

## Important Notes

- All code in English (variables, functions, comments)
- No emojis in code or documentation
- Professional code quality for portfolio/CV
- Infrastructure as Code using Python SDK
- All sensitive data in `.env` file (not committed to git)

## Cost Estimate

Approximate monthly cost for all Azure resources: $8-12 USD (Basic/Standard tiers)

## Author

Portfolio project for demonstrating Azure Data Engineering skills.
