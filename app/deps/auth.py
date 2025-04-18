from fastapi import HTTPException, Header
from app.core.supabase import supabase
from gotrue.types import User


def get_current_user(authorization: str = Header(...)) -> User:
    try:
        token = authorization.replace("Bearer ", "")
        result = supabase.auth.get_user(token)
        return result.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
