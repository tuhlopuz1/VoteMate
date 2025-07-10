import logging

from eth_account import Account
from fastapi import APIRouter
from uuid_v7.base import uuid7

from backend.core.dependencies import badresponse
from backend.models.cryptography import encrypt_secret
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.hashing import get_password_hash
from backend.models.redis_adapter import redis_adapter
from backend.models.schemas import UserCreate, UserRegResponse
from backend.models.token_manager import TokenManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/confirm-register/{code}", response_model=UserRegResponse)
async def register(user: UserCreate, code: str):
    username_check = await adapter.get_by_value(User, "username", user.username)
    if username_check:
        return badresponse("Username already exists", 409)
    redis_telegram = await redis_adapter.get(f"telegram-code:{code}")
    if not redis_telegram:
        return badresponse("Code is not valid", 401)
    db_tg = await adapter.get_by_value(User, "telegram_id", redis_telegram)
    if db_tg:
        return badresponse("Telegram is already used to create account", 409)
    new_id = uuid7()
    account = Account.create()
    private_key = account.key.hex()
    encrypted = encrypt_secret(private_key, user.password)
    new_user = {
        "id": new_id,
        "name": user.name,
        "username": f"@{user.username}",
        "hashed_password": get_password_hash(user.password),
        "role": user.role,
        "telegram_id": redis_telegram,
        "encrypted_key": encrypted,
    }

    new_user_db = await adapter.insert(User, new_user)

    access_token = TokenManager.create_token(
        {"sub": str(new_user_db.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = TokenManager.create_token(
        {"sub": str(new_user_db.id), "type": "refresh"},
        TokenManager.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return UserRegResponse(
        id=new_user_db.id,
        name=new_user_db.name,
        username=new_user_db.username,
        role=new_user_db.role,
        access_token=access_token,
        refresh_token=refresh_token,
        telegram_id=redis_telegram,
        private_key=private_key,
    )
