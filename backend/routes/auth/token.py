from fastapi import APIRouter, status

from backend.core.dependencies import badresponse
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.hashing import verify_password
from backend.models.schemas import Tokens, UserLogin
from backend.models.token_manager import TokenManager

router = APIRouter()


@router.post("/token", response_model=Tokens, status_code=status.HTTP_201_CREATED)
async def token(user: UserLogin):
    bd_user = await adapter.get_by_value(User, "username", f"@{user.identifier}")

    if bd_user == [] or bd_user is None:
        return badresponse("User not found", 404)

    bd_user = bd_user[0]

    if not verify_password(user.password, bd_user.hashed_password):
        return badresponse("Forbidden", 403)

    access_token = TokenManager.create_token(
        {"sub": str(bd_user.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_token = TokenManager.create_token(
        {"sub": str(bd_user.id), "type": "refresh"},
        TokenManager.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    tokens = Tokens(access_token=access_token, refresh_token=refresh_token)

    return tokens
