#!/usr/bin/env python3
"""
Simple test script to verify LocalStack integration
Run this after starting LocalStack to test the setup
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from app.services.aws_mock import mock_aws_service


def test_localstack_setup():
    """Test LocalStack setup and basic operations"""
    print("Testing LocalStack integration...")
    
    # Check if we're using LocalStack
    print(f"Using LocalStack: {mock_aws_service.use_localstack}")
    print(f"Endpoint URL: {mock_aws_service.endpoint_url}")
    
    if not mock_aws_service.use_localstack:
        print("Not using LocalStack - AWS credentials found")
        return
    
    try:
        # Test DynamoDB
        print("\nTesting DynamoDB...")
        dynamodb = mock_aws_service.get_dynamodb_resource()
        tables = list(dynamodb.tables.all())
        print(f"Available tables: {[table.name for table in tables]}")
        
        # Test S3
        print("\nTesting S3...")
        s3 = mock_aws_service.get_s3_client()
        buckets = s3.list_buckets()
        print(f"Available buckets: {[bucket['Name'] for bucket in buckets['Buckets']]}")
        
        print("\n✅ LocalStack integration test passed!")
        
    except Exception as e:
        print(f"\n❌ LocalStack integration test failed: {e}")
        print("Make sure LocalStack is running: docker-compose up localstack")


if __name__ == "__main__":
    test_localstack_setup()
