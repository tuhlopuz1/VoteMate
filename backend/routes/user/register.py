from fastapi import APIRouter
from fastapi.responses import JSONResponse
from uuid_v7.base import uuid7

from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.hashing import get_password_hash
from backend.models.schemas import UserRegister

router = APIRouter()


@router.post("/register")
async def register(user: UserRegister):
    user_db = await adapter.get_by_value(User, "username", user.username)
    if user_db:
        return JSONResponse({"message": "User already registered"}, status_code=409)
    uuid = uuid7
    new_user = {
        "id": uuid,
        "username": user.username,
        "password_hash": get_password_hash(user.password),
    }

    await adapter.insert(User, new_user)
    return JSONResponse({"message": "success"})
