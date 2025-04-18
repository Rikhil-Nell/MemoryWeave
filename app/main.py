import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import auth_router
from app.api.v1.video import video_router

from app.deps.auth import get_current_user
from app.core.constants import UPLOAD_DIR

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/me")
def get_me(user=Depends(get_current_user)):
    return user


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(video_router, prefix="/api/v1/video", tags=["video"])
