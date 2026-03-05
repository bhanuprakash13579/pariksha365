import boto3
from app.core.config import settings
import json
import uuid

class R2StorageService:
    def __init__(self):
        # We will configure these in .env later once the user provides them
        self.endpoint_url = settings.R2_ENDPOINT_URL
        self.access_key = settings.R2_ACCESS_KEY_ID
        self.secret_key = settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.R2_BUCKET_NAME
        self.public_domain = settings.R2_PUBLIC_DOMAIN

        # Boto3 client configured for Cloudflare R2
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            # R2 doesn't use standard regions, but boto3 requires the argument
            region_name='auto'
        )

    async def upload_test_json(self, test_id: str, test_data: dict) -> str:
        """
        Uploads a compiled mock test JSON directly to Cloudflare R2
        Returns the public CDN URL for the frontend to consume.
        """
        file_key = f"tests/{test_id}/{uuid.uuid4()}.json"
        
        # Convert dict to JSON string
        json_string = json.dumps(test_data)
        
        # Upload using standard S3 protocol
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=file_key,
            Body=json_string,
            ContentType='application/json'
        )
        
        # Return the public URL
        return f"{self.public_domain}/{file_key}"

r2_storage = R2StorageService()
