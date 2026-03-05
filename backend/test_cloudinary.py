import os
# Set env var BEFORE importing cloudinary
os.environ["CLOUDINARY_URL"] = "cloudinary://591914115337595:t6n8XkVBH8vfCxs3YkThwVF18fM@dn6hpzkah"

import cloudinary
import cloudinary.uploader

try:
    print("Testing Cloudinary upload...")
    # Create a tiny 1x1 GIF in memory to upload
    tiny_gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    
    result = cloudinary.uploader.upload(
        tiny_gif,
        folder="test_folder", 
        resource_type="image"
    )
    print("SUCCESS! Uploaded to:", result.get("secure_url"))
except Exception as e:
    print("ERROR:", e)
