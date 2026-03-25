import os
import uuid
import requests
from fastapi import UploadFile
from dotenv import load_dotenv
from typing import Union

import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

UPLOAD_DIR = "uploads"
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")

if STORAGE_TYPE == "cloudinary":
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def upload_image(file_or_url: Union[UploadFile, str]) -> str:
    """
    Saves an image (either a file or a URL) to Cloudinary or the local 'uploads' directory.
    Returns the URL/path to the image.
    """
    if STORAGE_TYPE == "cloudinary":
        try:
            if isinstance(file_or_url, str):
                # Upload from URL
                result = cloudinary.uploader.upload(file_or_url)
                return result.get("secure_url")
            else:
                # Upload from File (read bytes)
                content = await file_or_url.read()
                result = cloudinary.uploader.upload(content)
                return result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")
            raise Exception(f"Failed to upload image to Cloudinary. Error: {str(e)}")

    # Fallback to local storage
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.jpg" # Defaulting to .jpg for simplicity or extracting from content type/URL
    file_path = os.path.join(UPLOAD_DIR, filename)

    if isinstance(file_or_url, str):
        # Handle URL: Download the image
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(file_or_url, stream=True, timeout=15, headers=headers)
            response.raise_for_status()
            
            # Try to get extension from URL or Content-Type
            ext = os.path.splitext(file_or_url.split('?')[0])[1]
            if not ext:
                content_type = response.headers.get('Content-Type', '')
                if 'image/png' in content_type: ext = '.png'
                elif 'image/jpeg' in content_type: ext = '.jpg'
                elif 'image/gif' in content_type: ext = '.gif'
                elif 'image/webp' in content_type: ext = '.webp'
                else: ext = '.jpg'
            
            filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return f"/uploads/{filename}"
        except Exception as e:
            print(f"Error downloading image from {file_or_url}: {e}")
            raise Exception(f"Failed to download image from URL. Error: {str(e)}")
    else:
        # Handle File Upload
        ext = os.path.splitext(file_or_url.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(await file_or_url.read())
        
        return f"/uploads/{filename}"
