import os
import boto3
import uuid
import config

class StorageService:
    """Storage service that works locally or in AWS"""
    
    def __init__(self):
        self.env = os.environ.get('ENVIRONMENT', 'local')
        self.s3_bucket = os.environ.get('S3_BUCKET', 'menu-maestro-images')
    
    def save_image(self, image_bytes, image_id=None):
        """Save an image to storage and return its path/URL"""
        if image_id is None:
            image_id = str(uuid.uuid4())
            
        if config.USE_S3:
            # S3 implementation
            s3_client = boto3.client('s3')
            key = f"uploads/{image_id}.jpg"
            s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=image_bytes
            )
            return f"s3://{self.s3_bucket}/{key}"
        else:
            # Local filesystem implementation
            os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
            local_path = f"{config.UPLOAD_FOLDER}/{image_id}.jpg"
            with open(local_path, 'wb') as f:
                f.write(image_bytes)
            return local_path
    
    def get_image(self, path_or_key):
        """Get image bytes from storage"""
        if path_or_key.startswith('s3://'):
            # S3 implementation
            s3_client = boto3.client('s3')
            bucket = path_or_key.split('/')[2]
            key = '/'.join(path_or_key.split('/')[3:])
            response = s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        else:
            # Local filesystem implementation
            with open(path_or_key, 'rb') as f:
                return f.read()