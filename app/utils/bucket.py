import json
import os

from app.core.supabase import supabase
from datetime import datetime

BUCKET_NAME = "images"
JSON_FILE = "captured_images.json"


async def push_images_to_supabase_and_log(timeline_id: str):
    try:
        with open(JSON_FILE, "r") as f:
            image_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    for class_id, data in image_log.items():
        local_path = data["path"]
        filename = os.path.basename(local_path)
        storage_path = f"frames/{filename}"

        # Upload to Supabase storage
        with open(local_path, "rb") as f:
            response = supabase.storage.from_(BUCKET_NAME).upload(
                storage_path, f, file_options={"x-upsert": "true"}
            )

            if hasattr(response, 'error'):
                print(f"Failed to upload {filename}: {response.error}")
            elif hasattr(response, 'status_code') and response.status_code != 200:
                print(
                    f"Failed to upload {filename}: Status code {response.status_code}")
            elif hasattr(response, 'message'):
                print(f"Failed to upload {filename}: {response.message}")
            else:
                print(f"Upload for {filename} succeeded")

        # Get public URL
        public_url = supabase.storage.from_(
            BUCKET_NAME).get_public_url(storage_path)

        # Handle timestamp extraction
        try:
            timestamp_str = filename.split("_")[-1].split(".")[0]
            timestamp_obj = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f")
        except Exception as e:
            print(f"Invalid timestamp format in filename {filename}: {e}")
            continue

        # Now you can insert into the frame table
        supabase.table("frame").insert({
            "image_url": public_url,
            "timestamp": timestamp_obj.strftime("%H:%M:%S"),
            "timeline_id": timeline_id  # Use the provided timeline_id directly
        }).execute()
