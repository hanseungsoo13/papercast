"""Google Cloud Storage uploader service."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from google.cloud import storage

from src.utils.logger import logger
from src.utils.retry import retry_on_failure


class GCSUploader:
    """Uploads files to Google Cloud Storage."""
    
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        """Initialize the GCS uploader.
        
        Args:
            bucket_name: GCS bucket name
            credentials_path: Path to Google Cloud credentials JSON
        """
        self.logger = logger
        self.bucket_name = bucket_name
        
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    @retry_on_failure(max_attempts=3, exceptions=(Exception,))
    def upload_file(
        self,
        local_path: str,
        destination_path: str,
        content_type: str = "audio/mpeg",
        make_public: bool = True
    ) -> str:
        """Upload a file to GCS and generate signed URL.
        
        Args:
            local_path: Local file path
            destination_path: Destination path in GCS
            content_type: MIME type of the file
            make_public: Whether to make the file publicly accessible
            
        Returns:
            Signed URL valid for 7 days (accessible without authentication)
            
        Raises:
            FileNotFoundError: If local file doesn't exist
            Exception: If upload fails
        """
        local_file = Path(local_path)
        if not local_file.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        file_size = local_file.stat().st_size
        self.logger.info(f"Uploading {local_path} ({file_size} bytes) to gs://{self.bucket_name}/{destination_path}")
        
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(local_path, content_type=content_type)
            
            if make_public:
                try:
                    blob.make_public()
                    self.logger.info(f"File made public")
                except Exception as acl_error:
                    # Uniform bucket-level access enabled - skip individual ACL
                    self.logger.warning(f"Could not set individual ACL (uniform bucket-level access enabled): {acl_error}")
                    self.logger.info(f"File will be public if bucket has public access enabled")
            
            # Generate signed URL that works for 7 days
            from datetime import timedelta
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            self.logger.info(f"File uploaded successfully with signed URL")
            
            return signed_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload file to GCS: {e}")
            raise
    
    @retry_on_failure(max_attempts=3, exceptions=(Exception,))
    def upload_json(
        self,
        data: Dict[str, Any],
        destination_path: str,
        make_public: bool = True
    ) -> str:
        """Upload JSON data to GCS and generate signed URL.
        
        Args:
            data: Dictionary to upload as JSON
            destination_path: Destination path in GCS
            make_public: Whether to make the file publicly accessible
            
        Returns:
            Signed URL valid for 7 days (accessible without authentication)
            
        Raises:
            Exception: If upload fails
        """
        self.logger.info(f"Uploading JSON to gs://{self.bucket_name}/{destination_path}")
        
        try:
            blob = self.bucket.blob(destination_path)
            json_string = json.dumps(data, ensure_ascii=False, indent=2)
            blob.upload_from_string(json_string, content_type="application/json")
            
            if make_public:
                try:
                    blob.make_public()
                    self.logger.info(f"JSON made public")
                except Exception as acl_error:
                    # Uniform bucket-level access enabled - skip individual ACL
                    self.logger.warning(f"Could not set individual ACL (uniform bucket-level access enabled): {acl_error}")
                    self.logger.info(f"JSON will be public if bucket has public access enabled")
            
            # Generate signed URL that works for 7 days
            from datetime import timedelta
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            self.logger.info(f"JSON uploaded successfully with signed URL")
            
            return signed_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload JSON to GCS: {e}")
            raise
    
    def delete_file(self, file_path: str) -> None:
        """Delete a file from GCS.
        
        Args:
            file_path: Path to file in GCS
        """
        self.logger.info(f"Deleting gs://{self.bucket_name}/{file_path}")
        
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            self.logger.info(f"File deleted successfully")
        except Exception as e:
            self.logger.error(f"Failed to delete file from GCS: {e}")
            raise
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in GCS.
        
        Args:
            file_path: Path to file in GCS
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            blob = self.bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            self.logger.error(f"Failed to check file existence: {e}")
            return False
    
    def get_public_url(self, file_path: str) -> str:
        """Get public URL for a file in GCS.
        
        Args:
            file_path: Path to file in GCS
            
        Returns:
            Public URL
        """
        return f"https://storage.googleapis.com/{self.bucket_name}/{file_path}"
    
    def list_files(self, prefix: str = "") -> list[str]:
        """List files in GCS bucket with optional prefix.
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of file paths
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []

