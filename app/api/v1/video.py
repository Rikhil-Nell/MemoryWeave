import os
from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from gotrue.types import User

from app.core.supabase import supabase
from app.deps.auth import get_current_user
from app.core.constants import UPLOAD_DIR

video_router = APIRouter()


@video_router.post("/upload")
async def upload_video(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    filename = f"{datetime.now().isoformat().replace(':', '-')}_{user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"filename": filename, "message": "Upload successful"}
