"""
S3 Service Layer for reading AIS data from Amazon S3.
Handles all S3 operations including listing, fetching, and parsing JSON files.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Service:
    """Service class for interacting with Amazon S3."""
    
    def __init__(self):
        """Initialize S3 client using boto3.
        
        AWS credentials are automatically loaded from:
        - IAM role (when running on AWS Lambda/EC2)
        - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        - AWS credentials file (~/.aws/credentials)
        """
        try:
            self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
            self.bucket_name = settings.S3_BUCKET_NAME
            self.prefix = settings.S3_PREFIX
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure IAM role or environment variables.")
            raise
    
    def _list_objects(self, prefix: str) -> List[Dict[str, Any]]:
        """List all objects in S3 with the given prefix.
        
        Args:
            prefix: S3 key prefix to filter objects
            
        Returns:
            List of S3 object metadata dictionaries
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.warning(f"No objects found with prefix: {prefix}")
                return []
            
            return response['Contents']
        
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            raise
    
    def _get_object_content(self, key: str) -> Dict[str, Any]:
        """Fetch and parse JSON content from S3 object.
        
        Args:
            key: S3 object key
            
        Returns:
            Parsed JSON content as dictionary
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # Read and parse JSON content
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
            
            logger.info(f"Successfully fetched object: {key}")
            return data
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Object not found: {key}")
                raise FileNotFoundError(f"S3 object not found: {key}")
            else:
                logger.error(f"Error fetching S3 object: {e}")
                raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {key}: {e}")
            raise ValueError(f"Invalid JSON in S3 object: {key}")
    
    def get_vessel_records(self, mmsi: str) -> List[Dict[str, Any]]:
        """Fetch all processed AIS records for a given MMSI.
        
        Args:
            mmsi: Maritime Mobile Service Identity
            
        Returns:
            List of AIS record dictionaries
        """
        # Construct prefix to search for files related to this MMSI
        # Files might be named with MMSI or contain MMSI in the data
        vessel_prefix = self.prefix
        
        # List all objects with the base prefix
        objects = self._list_objects(vessel_prefix)
        
        if not objects:
            logger.warning(f"No objects found for MMSI: {mmsi}")
            return []
        
        # Fetch and filter records
        records = []
        for obj in objects:
            try:
                # Skip directories (keys ending with /)
                if obj['Key'].endswith('/'):
                    continue
                
                # Fetch object content
                data = self._get_object_content(obj['Key'])
                
                # Check if this record matches the MMSI
                # Handle both single record and list of records
                if isinstance(data, dict):
                    if data.get('mmsi') == mmsi:
                        records.append(data)
                elif isinstance(data, list):
                    for record in data:
                        if isinstance(record, dict) and record.get('mmsi') == mmsi:
                            records.append(record)
            
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Skipping object {obj['Key']}: {e}")
                continue
        
        return records
    
    def get_latest_vessel_record(self, mmsi: str) -> Optional[Dict[str, Any]]:
        """Fetch the most recent AIS record for a given MMSI.
        
        Args:
            mmsi: Maritime Mobile Service Identity
            
        Returns:
            Latest AIS record dictionary or None if not found
        """
        records = self.get_vessel_records(mmsi)
        
        if not records:
            return None
        
        # Sort records by timestamp (most recent first)
        sorted_records = self._sort_records_by_timestamp(records, descending=True)
        
        return sorted_records[0] if sorted_records else None
    
    def _sort_records_by_timestamp(
        self, 
        records: List[Dict[str, Any]], 
        descending: bool = False
    ) -> List[Dict[str, Any]]:
        """Sort AIS records by timestamp.
        
        Args:
            records: List of AIS record dictionaries
            descending: If True, sort in descending order (newest first)
            
        Returns:
            Sorted list of records
        """
        def parse_timestamp(record: Dict[str, Any]) -> datetime:
            """Parse ISO 8601 timestamp from record."""
            try:
                timestamp_str = record.get('timestamp', '')
                # Handle different ISO 8601 formats
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str[:-1] + '+00:00'
                return datetime.fromisoformat(timestamp_str)
            except (ValueError, AttributeError):
                logger.warning(f"Invalid timestamp in record: {record.get('timestamp')}")
                # Return epoch for invalid timestamps (will be sorted last)
                return datetime.fromtimestamp(0)
        
        return sorted(records, key=parse_timestamp, reverse=descending)
    
    def get_vessel_history(self, mmsi: str) -> List[Dict[str, Any]]:
        """Fetch all AIS records for a vessel, sorted by timestamp.
        
        Args:
            mmsi: Maritime Mobile Service Identity
            
        Returns:
            List of AIS records sorted by timestamp (oldest to newest)
        """
        records = self.get_vessel_records(mmsi)
        
        if not records:
            return []
        
        # Sort by timestamp (ascending order)
        return self._sort_records_by_timestamp(records, descending=False)
    
    def get_vessel_esg_data(self, mmsi: str) -> Optional[Dict[str, Any]]:
        """Fetch ESG-specific data for a vessel (latest record).
        
        Args:
            mmsi: Maritime Mobile Service Identity
            
        Returns:
            Dictionary with MMSI, CO2, ESG score, and timestamp
        """
        latest_record = self.get_latest_vessel_record(mmsi)
        
        if not latest_record:
            return None
        
        # Extract only ESG-relevant fields
        return {
            'mmsi': latest_record.get('mmsi'),
            'estimated_co2_kg': latest_record.get('estimated_co2_kg'),
            'esg_environment_score': latest_record.get('esg_environment_score'),
            'timestamp': latest_record.get('timestamp')
        }


# Create a global S3 service instance
s3_service = S3Service()
