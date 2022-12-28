import boto3

from Documents.constants.storage import STORAGE_BUCKET_NAME

os = boto3.client(
    's3',
    aws_access_key_id='<aws_access_key_id>',
    aws_secret_access_key='<aws_secret_access_key>',
    region_name="ru-central1",
    endpoint_url="https://storage.yandexcloud.net/"
)


def upload_to_storage(file, key_name: str, bucket: str = STORAGE_BUCKET_NAME):
    file.seek(0)
    os.upload_fileobj(file, bucket, key_name)


def delete_from_storage(key_name: str, bucket: str = STORAGE_BUCKET_NAME):
    os.delete_object(Bucket=bucket, Key=key_name)
