from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from app.services.aws_mock import mock_aws_service


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint that includes LocalStack status"""
    
    health_status = {
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z',  # You can use timezone.now() here
        'services': {
            'django': 'healthy',
            'database': 'healthy',  # You can add actual DB health check here
            'redis': 'healthy',     # You can add actual Redis health check here
        }
    }
    
    # Check LocalStack status if it's being used
    if mock_aws_service.use_localstack:
        try:
            # Test DynamoDB connection
            dynamodb = mock_aws_service.get_dynamodb_resource()
            tables = list(dynamodb.tables.all())
            
            # Test S3 connection
            s3 = mock_aws_service.get_s3_client()
            buckets = s3.list_buckets()
            
            health_status['services']['localstack'] = 'healthy'
            health_status['localstack'] = {
                'endpoint': mock_aws_service.endpoint_url,
                'dynamodb_tables': len(tables),
                's3_buckets': len(buckets['Buckets'])
            }
            
        except Exception as e:
            health_status['services']['localstack'] = 'unhealthy'
            health_status['localstack_error'] = str(e)
            health_status['status'] = 'degraded'
    
    # Check if using real AWS
    else:
        health_status['services']['aws'] = 'configured'
        health_status['aws'] = {
            'region': 'us-east-1',
            'services': ['dynamodb', 's3']
        }
    
    return Response(health_status, status=status.HTTP_200_OK)
