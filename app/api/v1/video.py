import os
from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from gotrue.types import User

from app.core.supabase import supabase
from app.deps.auth import get_current_user
from app.core.constants import UPLOAD_DIR, PROJECT_PATH

video_router = APIRouter()


@video_router.post("/upload")
async def upload_video(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    try:
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        filename = f"{datetime.now().isoformat().replace(':', '-')}_{user.id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        supabase.table("video").insert({"user_id": user.id, "file_location": f"{PROJECT_PATH}\\videos\\{filename}"}).execute()

        return {"filename": filename, "message": "Upload successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")