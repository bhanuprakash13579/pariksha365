import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def test_r2_upload():
    print("Testing R2 Upload to specific bucket...")
    endpoint = os.getenv("R2_ENDPOINT_URL")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    bucket = os.getenv("R2_BUCKET_NAME")
    
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto' # Cloudflare standard
    )
    
    try:
        # Try to just put a tiny text file to see if we have write access
        response = s3.put_object(
            Bucket=bucket,
            Key="test_connection.txt",
            Body=b"Connection successful!",
            ContentType="text/plain"
        )
        print("SUCCESS! File uploaded to bucket:", bucket)
    except Exception as e:
        print("ERROR uploading to bucket:", type(e).__name__, str(e))

if __name__ == "__main__":
    test_r2_upload()
