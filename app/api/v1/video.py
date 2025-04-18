import os
from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from gotrue.types import User

from app.core.supabase import supabase
from app.deps.auth import get_current_user
from app.core.constants import UPLOAD_DIR, PROJECT_PATH
from app.core.agents import journal_agent
from app.core.parser import summarize_detected_objects

video_router = APIRouter()


@video_router.post("/upload")
async def upload_video(
    prompt: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    try:
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        filename = f"{datetime.now().isoformat().replace(':', '-')}_{user.id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        response = supabase.table("video").insert(
            {"user_id": user.id, "file_location": f"{PROJECT_PATH}\\videos\\{filename}"}).execute()

        supabase.table("timeline").insert(
            {"video_id": response.data[0]["id"], "story": (await summarize_detected_objects(response.data[0]["file_location"], prompt)).output}).execute()

        return {"filename": filename, "message": "story cooked successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
