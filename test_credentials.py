#!/usr/bin/env python3
"""Test script for Google Cloud credentials setup."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.credentials import setup_gcp_credentials_from_base64, validate_gcp_credentials_file


def test_credentials():
    """Test credential setup and validation."""
    print("🧪 Testing Google Cloud credentials setup...")
    
    # Test 1: Check if GCP_SERVICE_ACCOUNT_KEY is set
    base64_key = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
    if not base64_key:
        print("❌ GCP_SERVICE_ACCOUNT_KEY environment variable not set")
        print("   Set it with: export GCP_SERVICE_ACCOUNT_KEY='your_base64_encoded_key'")
        return False
    
    print(f"✅ GCP_SERVICE_ACCOUNT_KEY found (length: {len(base64_key)})")
    
    # Test 2: Try to decode and setup credentials
    print("\n🔑 Testing base64 decoding and credential setup...")
    if setup_gcp_credentials_from_base64(base64_key, "test_credentials.json"):
        print("✅ Credential setup successful")
    else:
        print("❌ Credential setup failed")
        return False
    
    # Test 3: Validate the created file
    print("\n🔍 Testing credential file validation...")
    if validate_gcp_credentials_file("test_credentials.json"):
        print("✅ Credential validation successful")
    else:
        print("❌ Credential validation failed")
        return False
    
    # Test 4: Check environment variable
    print(f"\n📁 GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Cleanup
    if Path("test_credentials.json").exists():
        Path("test_credentials.json").unlink()
        print("🧹 Cleaned up test file")
    
    print("\n🎉 All tests passed!")
    return True


if __name__ == "__main__":
    success = test_credentials()
    sys.exit(0 if success else 1)
