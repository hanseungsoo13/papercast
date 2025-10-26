"""Utility functions for handling Google Cloud credentials."""

import base64
import json
import os
from pathlib import Path
from typing import Optional

from src.utils.logger import logger


def setup_gcp_credentials_from_base64(
    base64_key: str, 
    output_path: str = "credentials/service-account.json"
) -> bool:
    """Set up Google Cloud credentials from base64 encoded JSON.
    
    Args:
        base64_key: Base64 encoded service account JSON
        output_path: Path to save the decoded JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Decode base64
        logger.info("Decoding base64 encoded service account key...")
        decoded_bytes = base64.b64decode(base64_key)
        
        # Parse as JSON to validate
        try:
            service_account_data = json.loads(decoded_bytes.decode('utf-8'))
            logger.info(f"✅ Valid service account JSON decoded")
            logger.info(f"📄 Project ID: {service_account_data.get('project_id', 'Not found')}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in decoded data: {e}")
            return False
        except UnicodeDecodeError as e:
            logger.error(f"❌ Invalid UTF-8 in decoded data: {e}")
            return False
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(decoded_bytes)
        
        logger.info(f"✅ Service account file saved to: {output_path}")
        
        # Set environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path(output_path).absolute())
        logger.info(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup GCP credentials: {e}")
        return False


def validate_gcp_credentials_file(credentials_path: str) -> bool:
    """Validate Google Cloud credentials file.
    
    Args:
        credentials_path: Path to credentials JSON file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if not Path(credentials_path).exists():
            logger.error(f"❌ Credentials file not found: {credentials_path}")
            return False
        
        with open(credentials_path, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.error(f"❌ Missing required fields in credentials: {missing_fields}")
            return False
        
        if data.get('type') != 'service_account':
            logger.error(f"❌ Invalid credentials type: {data.get('type')}")
            return False
        
        logger.info(f"✅ Valid service account credentials")
        logger.info(f"📄 Project ID: {data.get('project_id')}")
        logger.info(f"📧 Client Email: {data.get('client_email')}")
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in credentials file: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error validating credentials: {e}")
        return False


def setup_gcp_credentials_from_env() -> bool:
    """Set up GCP credentials from environment variables.
    
    This function handles both direct file paths and base64 encoded keys.
    
    Returns:
        True if successful, False otherwise
    """
    # Check for base64 encoded key first
    base64_key = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
    if base64_key:
        logger.info("🔑 Found base64 encoded GCP service account key")
        return setup_gcp_credentials_from_base64(base64_key)
    
    # Check for direct file path
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        logger.info(f"📁 Found GCP credentials file path: {credentials_path}")
        return validate_gcp_credentials_file(credentials_path)
    
    logger.error("❌ No GCP credentials found in environment variables")
    logger.error("   Set either GCP_SERVICE_ACCOUNT_KEY (base64) or GOOGLE_APPLICATION_CREDENTIALS (file path)")
    return False
