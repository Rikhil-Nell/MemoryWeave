from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.core.supabase import supabase

auth_router = APIRouter()


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


@auth_router.post("/signup")
def signup(data: AuthRequest):
    try:
        result = supabase.auth.sign_up(
            {"email": data.email, "password": data.password})

        return {"message": "Check your email to confirm signup", "user": result.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/login")
def login(data: AuthRequest):
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password})

        return {
            "access_token": result.session.access_token,
            "user": result.user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
