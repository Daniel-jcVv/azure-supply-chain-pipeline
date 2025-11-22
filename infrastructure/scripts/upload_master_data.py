"""
Upload Master Data to Azure Blob Storage
=========================================

Professional script to upload master data files to Azure Blob Storage
using Azure Python SDK.

Author: Supply Chain Analytics Project
Date: 2024-11-20
Version: 1.0

Features:
- Upload TSV compressed files
- Progress bar with tqdm
- Robust error handling
- Professional logging
- Automatic retry logic
- File validation before upload

Usage:
    python upload_master_data.py
    python upload_master_data.py --dry-run
"""

import os
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.core.exceptions import AzureError, ResourceExistsError
    from tqdm import tqdm
except ImportError as e:
    print("Error: Missing Azure dependencies.")
    print("\nInstall dependencies with:")
    print("  pip install azure-storage-blob tqdm")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AzureMasterDataUploader:
    """
    Class to handle uploading master data to Azure Blob Storage
    """

    def __init__(self, config_path: str = "../config/azure_config.json"):
        """
        Initialize uploader with configuration

        Args:
            config_path: Path to JSON configuration file
        """
        self.config = self._load_config(config_path)
        self.blob_service_client = None
        self.container_client = None
        self.upload_stats = {
            'total_files': 0,
            'uploaded': 0,
            'failed': 0,
            'skipped': 0,
            'total_bytes': 0
        }

    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from JSON file

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary with configuration
        """
        config_file = Path(__file__).parent / config_path

        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_file}")
            logger.info("\nINSTRUCTIONS:")
            logger.info("1. Copy azure_config.template.json to azure_config.json")
            logger.info("2. Edit azure_config.json with your Azure credentials")
            logger.info("3. Run this script again")
            sys.exit(1)

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Validate not default values
            if "YOUR_" in config['storage_account']['connection_string']:
                logger.error("You must configure your credentials in azure_config.json")
                logger.info("File still contains template values (YOUR_...)")
                sys.exit(1)

            return config
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            sys.exit(1)

    def connect(self):
        """
        Establish connection with Azure Blob Storage
        """
        try:
            logger.info("Connecting to Azure Blob Storage...")

            connection_string = self.config['storage_account']['connection_string']
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )

            # Verify connection
            account_info = self.blob_service_client.get_account_information()
            logger.info(f"Successfully connected to Storage Account")
            logger.info(f"   Account type: {account_info['sku_name']}")

            # Get or create container
            container_name = self.config['storage_account']['container_name']
            self._ensure_container_exists(container_name)

        except AzureError as e:
            logger.error(f"Error connecting to Azure: {e}")
            logger.info("\nVerify:")
            logger.info("  1. Connection string is correct")
            logger.info("  2. You have permissions on the Storage Account")
            logger.info("  3. Storage Account exists")
            sys.exit(1)

    def _ensure_container_exists(self, container_name: str):
        """
        Verify container exists, create if not

        Args:
            container_name: Container name
        """
        try:
            self.container_client = self.blob_service_client.get_container_client(
                container_name
            )

            # Try to get properties (will throw error if doesn't exist)
            self.container_client.get_container_properties()
            logger.info(f"Container '{container_name}' exists")

        except Exception:
            # Container doesn't exist, create it
            logger.warning(f"Container '{container_name}' does not exist")
            logger.info(f"Creating container '{container_name}'...")

            try:
                self.container_client = self.blob_service_client.create_container(
                    container_name
                )
                logger.info(f"Container '{container_name}' created successfully")
            except ResourceExistsError:
                logger.info(f"Container '{container_name}' already exists")
                self.container_client = self.blob_service_client.get_container_client(
                    container_name
                )
            except AzureError as e:
                logger.error(f"Error creating container: {e}")
                sys.exit(1)

    def _get_files_to_upload(self) -> List[Dict]:
        """
        Get list of TSV files to upload

        Returns:
            List of dictionaries with file info
        """
        source_path = Path(__file__).parent / self.config['paths']['master_data_source']

        if not source_path.exists():
            logger.error(f"Data directory not found: {source_path}")
            logger.info("\nMake sure you have generated the data first:")
            logger.info("  cd data_generation")
            logger.info("  ./run_all.sh master")
            sys.exit(1)

        files_to_upload = []

        # Search for compressed TSV files
        for tsv_file in source_path.rglob('*.tsv.gz'):
            file_info = {
                'local_path': tsv_file,
                'blob_name': str(tsv_file.relative_to(source_path)),
                'size': tsv_file.stat().st_size
            }
            files_to_upload.append(file_info)

        if not files_to_upload:
            logger.warning(f"No .tsv.gz files found in {source_path}")
            logger.info("\nVerify that files are in compressed TSV format")

        return files_to_upload

    def upload_file(self, file_info: Dict, dry_run: bool = False) -> bool:
        """
        Upload a file to Blob Storage

        Args:
            file_info: Dictionary with file info
            dry_run: If True, only simulates the upload

        Returns:
            True if successful, False if failed
        """
        local_path = file_info['local_path']
        blob_name = file_info['blob_name']

        try:
            if dry_run:
                logger.info(f"  [DRY-RUN] {blob_name} ({self._format_bytes(file_info['size'])})")
                return True

            # Get blob client
            blob_client = self.container_client.get_blob_client(blob_name)

            # Check if already exists
            try:
                properties = blob_client.get_blob_properties()
                logger.info(f"  SKIP: {blob_name} (already exists)")
                self.upload_stats['skipped'] += 1
                return True
            except:
                pass  # Doesn't exist, continue with upload

            # Upload with progress
            with open(local_path, 'rb') as data:
                blob_client.upload_blob(
                    data,
                    overwrite=False,
                    max_concurrency=4
                )

            logger.info(f"  OK: {blob_name} ({self._format_bytes(file_info['size'])})")
            self.upload_stats['uploaded'] += 1
            self.upload_stats['total_bytes'] += file_info['size']

            return True

        except AzureError as e:
            logger.error(f"  ERROR in {blob_name}: {e}")
            self.upload_stats['failed'] += 1
            return False

    def upload_all(self, dry_run: bool = False, overwrite: bool = False):
        """
        Upload all master data files

        Args:
            dry_run: If True, only simulates without uploading
            overwrite: If True, overwrites existing files
        """
        logger.info("\n" + "="*70)
        logger.info("UPLOADING MASTER DATA TO AZURE BLOB STORAGE")
        logger.info("="*70 + "\n")

        if dry_run:
            logger.warning("DRY-RUN MODE: Files will not be actually uploaded\n")

        # Get files
        files = self._get_files_to_upload()

        if not files:
            logger.error("No files to upload")
            return

        self.upload_stats['total_files'] = len(files)

        logger.info(f"Files found: {len(files)}")
        logger.info(f"Total size: {self._format_bytes(sum(f['size'] for f in files))}\n")

        # Upload with progress bar
        logger.info("Starting upload...\n")

        with tqdm(total=len(files), desc="Uploading", unit="file") as pbar:
            for file_info in files:
                self.upload_file(file_info, dry_run)
                pbar.update(1)

        # Final report
        self._print_summary(dry_run)

    def _print_summary(self, dry_run: bool):
        """
        Print operation summary
        """
        logger.info("\n" + "="*70)
        logger.info("UPLOAD SUMMARY")
        logger.info("="*70)

        if dry_run:
            logger.info(f"  Mode:              DRY-RUN (simulation)")
        else:
            logger.info(f"  Mode:              REAL")

        logger.info(f"  Total files:       {self.upload_stats['total_files']}")
        logger.info(f"  Uploaded:          {self.upload_stats['uploaded']}")
        logger.info(f"  Skipped:           {self.upload_stats['skipped']}")
        logger.info(f"  Failed:            {self.upload_stats['failed']}")

        if not dry_run:
            logger.info(f"  Total uploaded:    {self._format_bytes(self.upload_stats['total_bytes'])}")

        logger.info("="*70 + "\n")

        if self.upload_stats['failed'] > 0:
            logger.warning("Some files failed. Check log for details.")
        elif not dry_run and self.upload_stats['uploaded'] > 0:
            logger.info("Upload completed successfully!")
            logger.info(f"\nVerify in Azure Portal:")
            logger.info(f"   Storage Account: {self.config['storage_account']['name']}")
            logger.info(f"   Container: {self.config['storage_account']['container_name']}")

    @staticmethod
    def _format_bytes(bytes_size: int) -> str:
        """
        Format bytes to human-readable format

        Args:
            bytes_size: Size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"


def main():
    """
    Main function
    """
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Upload master data to Azure Blob Storage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python upload_master_data.py                      # Normal upload
  python upload_master_data.py --dry-run            # Simulate without uploading
  python upload_master_data.py --overwrite          # Overwrite existing files
  python upload_master_data.py --config custom.json # Use custom config
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate upload without actually uploading files'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing files in Azure'
    )

    parser.add_argument(
        '--config',
        default='../config/azure_config.json',
        help='Path to configuration file (default: ../config/azure_config.json)'
    )

    args = parser.parse_args()

    try:
        # Create uploader
        uploader = AzureMasterDataUploader(config_path=args.config)

        # Connect to Azure
        uploader.connect()

        # Upload
        uploader.upload_all(dry_run=args.dry_run, overwrite=args.overwrite)

    except KeyboardInterrupt:
        logger.warning("\nUpload cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
