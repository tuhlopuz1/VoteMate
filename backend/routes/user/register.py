from uuid import UUID, uuid5

from core.config import UUID_SHA
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.db_adapter import adapter
from models.db_tables import User
from models.hashing import get_password_hash
from models.schemas import UserRegister

router = APIRouter()


@router.post("/register")
async def register(user: UserRegister):
    user_db = await adapter.get_by_value(User, "username", user.username)
    if user_db:
        return JSONResponse({"message": "User already registered"}, status_code=409)
    id = uuid5(UUID(UUID_SHA), user.username)
    new_user = {
        "id": id,
        "username": user.username,
        "password_hash": get_password_hash(user.password),
    }

    await adapter.insert(User, new_user)
    return JSONResponse({"message": "success"})
