import os
from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from gotrue.types import User

from app.core.supabase import supabase
from app.deps.auth import get_current_user
from app.core.constants import UPLOAD_DIR, PROJECT_PATH
from app.core.agents import journal_agent
from app.core.parser import summarize_detected_objects
from app.utils.bucket import push_images_to_supabase_and_log

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

        timeline = supabase.table("timeline").insert(
            {"video_id": response.data[0]["id"], "story": (await summarize_detected_objects(response.data[0]["file_location"], prompt)).output}).execute()

        await push_images_to_supabase_and_log(timeline.data[0]["id"])

        return {"filename": filename, "message": "story cooked successfully", "timeline_id": timeline.data[0]["id"]}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@video_router.get("/")
async def get_timelines(user: User = Depends(get_current_user)):
    try:
        response = supabase.table("timeline").select(
            "id, story, title, video_id, video(created_at, user_id)"
        ).eq("video.user_id", user.id).order("created_at", desc=True).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="No videos found")

        return response.data
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Retrieval failed: {str(e)}")


@video_router.get("/timeline/{timeline_id}")
async def get_timeline_and_frames_by_id(timeline_id: str, user: User = Depends(get_current_user)):
    try:
        response = supabase.table("timeline").select(
            "id, story, title, video_id, video(user_id), frame(id, image_url, timestamp)"
        ).eq("id", timeline_id).eq("video.user_id", user.id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="No videos found")

        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Retrieval failed: {str(e)}")
