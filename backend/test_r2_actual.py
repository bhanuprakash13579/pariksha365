import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.r2_storage_service import r2_storage

async def test_r2_service():
    print("Testing actual R2StorageService...")
    test_id = "test-1234-abcd"
    test_data = {"questions": [{"id": 1, "text": "What is 2+2?", "answer": 4}]}
    
    try:
        url = await r2_storage.upload_test_json(test_id, test_data)
        print("SUCCESS! Test uploaded. Public URL:")
        print(url)
    except Exception as e:
        print("ERROR uploading via service:", type(e).__name__, str(e))

if __name__ == "__main__":
    asyncio.run(test_r2_service())
