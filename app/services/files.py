import boto3
from cachetools import TTLCache, cached
from django.conf import settings


@cached(TTLCache(maxsize=1, ttl=60 * 60))
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def generate_presigned_url(upload_path, file_name, file_type):
    s3_client = get_s3_client()

    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": upload_path,
            "ContentType": file_type,
            "Metadata": {"file_name": file_name},
        },
        ExpiresIn=settings.AWS_S3_EXPIRATION_TIME,
    )

    return presigned_url


def generate_get_presigned_url(file_name):
    s3_client = get_s3_client()

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_name},
        ExpiresIn=settings.AWS_S3_EXPIRATION_TIME,
    )

    return presigned_url


def remove_file(file_name):
    s3_client = get_s3_client()

    return s3_client.delete_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name
    )


def generate_download_url(file_name):
    s3_client = get_s3_client()

    download_url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file_name,
            "ResponseContentType": "application/octet-stream",
        },
        ExpiresIn=settings.AWS_S3_EXPIRATION_TIME,
    )

    return download_url
