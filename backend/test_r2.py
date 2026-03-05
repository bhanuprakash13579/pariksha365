import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def test_r2():
    print("Testing R2 Connection...")
    endpoint = os.getenv("R2_ENDPOINT_URL")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    
    print(f"Endpoint: {endpoint}")
    print(f"Access Key (first 4): {access_key[:4] if access_key else None}")
    
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto' # Cloudflare standard
    )
    
    try:
        response = s3.list_buckets()
        print("Successfully connected! Buckets found:")
        for bucket in response.get('Buckets', []):
            print(f" - {bucket['Name']}")
    except Exception as e:
        print("ERROR listing buckets:", type(e).__name__, str(e))

if __name__ == "__main__":
    test_r2()
