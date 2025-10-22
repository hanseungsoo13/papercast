#!/usr/bin/env python3
"""Make GCS bucket publicly accessible."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from google.cloud import storage
from src.utils.config import Config

def make_bucket_public():
    """Make the GCS bucket publicly accessible."""
    config = Config()
    bucket_name = config.get("GCS_BUCKET_NAME")
    
    if not bucket_name:
        print("❌ Error: GCS_BUCKET_NAME not set in .env")
        return False
    
    print(f"🔧 Making bucket '{bucket_name}' publicly accessible...")
    
    try:
        # Initialize storage client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Get current IAM policy
        policy = bucket.get_iam_policy(requested_policy_version=3)
        
        # Add public read access
        # For uniform bucket-level access, we need to add allUsers to the IAM policy
        print("📝 Adding allUsers:objectViewer role...")
        policy.bindings.append({
            "role": "roles/storage.objectViewer",
            "members": {"allUsers"}
        })
        
        # Set the updated policy
        bucket.set_iam_policy(policy)
        
        print("✅ Success! Bucket is now publicly accessible.")
        print(f"🌐 Files will be accessible at: https://storage.googleapis.com/{bucket_name}/...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 대안 방법:")
        print("1. GCP Console에서 수동으로 설정:")
        print(f"   https://console.cloud.google.com/storage/browser/{bucket_name}")
        print("   → PERMISSIONS 탭 → GRANT ACCESS")
        print("   → New principals: allUsers")
        print("   → Role: Storage Object Viewer")
        print("\n2. 또는 gsutil 명령어 사용:")
        print(f"   gsutil iam ch allUsers:objectViewer gs://{bucket_name}")
        return False

if __name__ == "__main__":
    success = make_bucket_public()
    sys.exit(0 if success else 1)


