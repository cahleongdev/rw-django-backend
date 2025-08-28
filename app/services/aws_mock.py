import os
import boto3
from django.conf import settings
from typing import Optional, Dict, Any, List


class MockAWSService:
    """Mock AWS service that uses LocalStack endpoints when AWS credentials are not available"""
    
    def __init__(self):
        self.use_localstack = self._should_use_localstack()
        self.endpoint_url = self._get_endpoint_url()
        
    def _should_use_localstack(self) -> bool:
        """Check if we should use LocalStack (when AWS credentials are missing)"""
        # Check if we have real AWS credentials (not the "test" values from LocalStack)
        real_aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
        real_aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        return not (real_aws_key and real_aws_secret)
    
    def _get_endpoint_url(self) -> Optional[str]:
        """Get the endpoint URL for LocalStack"""
        if self.use_localstack:
            return os.environ.get('AWS_ENDPOINT_URL', 'http://localstack:4566')
        return None
    
    def get_dynamodb_resource(self):
        """Get DynamoDB resource with appropriate endpoint"""
        if self.use_localstack:
            return boto3.resource(
                'dynamodb',
                endpoint_url=self.endpoint_url,
                region_name='us-east-1',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
        else:
            return boto3.resource(
                'dynamodb',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name='us-east-1'
            )
    
    def get_dynamodb_client(self):
        """Get DynamoDB client with appropriate endpoint"""
        if self.use_localstack:
            return boto3.client(
                'dynamodb',
                endpoint_url=self.endpoint_url,
                region_name='us-east-1',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
        else:
            return boto3.client(
                'dynamodb',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name='us-east-1'
            )
    
    def get_s3_client(self):
        """Get S3 client with appropriate endpoint"""
        if self.use_localstack:
            return boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                region_name='us-east-1',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
        else:
            return boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
    
    def setup_localstack_resources(self):
        """Set up LocalStack resources (create tables, buckets)"""
        if not self.use_localstack:
            print("Not using LocalStack, skipping resource setup")
            return
            
        print(f"Setting up LocalStack resources with endpoint: {self.endpoint_url}")
        
        try:
            # Create DynamoDB table if it doesn't exist
            print("Setting up DynamoDB...")
            dynamodb = self.get_dynamodb_resource()
            table_name = settings.DYNAMODB_TABLE_NAME or 'notifications'
            print(f"Checking for DynamoDB table: {table_name}")
            
            try:
                table = dynamodb.Table(table_name)
                table.load()
                print(f"DynamoDB table {table_name} already exists")
            except Exception as e:
                print(f"Table {table_name} doesn't exist, creating it... Error: {e}")
                # Table doesn't exist, create it
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'id', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'id', 'AttributeType': 'S'},
                        {'AttributeName': 'created_at', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                print(f"Waiting for table {table_name} to be created...")
                table.wait_until_exists()
                print(f"Created DynamoDB table: {table_name}")
            
            # Create S3 bucket if it doesn't exist
            print("Setting up S3...")
            s3 = self.get_s3_client()
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME or 'test-bucket'
            print(f"Checking for S3 bucket: {bucket_name}")
            
            try:
                s3.head_bucket(Bucket=bucket_name)
                print(f"S3 bucket {bucket_name} already exists")
            except Exception as e:
                print(f"Bucket {bucket_name} doesn't exist, creating it... Error: {e}")
                # Bucket doesn't exist, create it
                # us-east-1 doesn't need LocationConstraint
                if settings.AWS_S3_REGION_NAME == 'us-east-1':
                    s3.create_bucket(Bucket=bucket_name)
                else:
                    s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': settings.AWS_S3_REGION_NAME}
                    )
                print(f"Created S3 bucket: {bucket_name}")
                
        except Exception as e:
            print(f"Warning: Could not set up LocalStack resources: {e}")
            print("Make sure LocalStack is running and accessible")


# Global instance
mock_aws_service = MockAWSService()
