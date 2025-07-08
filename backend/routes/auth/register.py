import logging

from fastapi import APIRouter
from uuid_v7.base import uuid7

from backend.core.dependencies import badresponse
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.hashing import get_password_hash
from backend.models.schemas import UserCreate, UserRegResponse
from backend.models.token_manager import TokenManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register")
async def register(user: UserCreate):
    username_check = await adapter.get_by_value(User, "username", user.username)
    if username_check:
        return badresponse("Username already exists", 409)
    new_id = uuid7()
    new_user = {
        "id": new_id,
        "name": user.name,
        "username": f"@{user.username}",
        "hashed_password": get_password_hash(user.password),
        "role": user.role,
        "description": user.description,
    }

    await adapter.insert(User, new_user)
    new_user_db = await adapter.get_by_id(User, new_id)

    access_token = TokenManager.create_token(
        {"sub": str(new_user_db.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return UserRegResponse(
        id=new_user_db.id,
        name=new_user_db.name,
        username=new_user_db.username,
        role=new_user_db.role,
        description=new_user_db.description,
        access_token=access_token,
    )
