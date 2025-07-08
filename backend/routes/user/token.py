from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.hashing import verify_password
from backend.models.schemas import Tokens, UserRegister
from backend.models.token_manager import TokenManager

router = APIRouter()


@router.post("/get-token", response_model=Tokens)
async def get_token(user: UserRegister):
    user_db = await adapter.get_by_value(User, "username", user.username)
    if not user_db:
        return JSONResponse(
            content={"message": "Invalid credentials", "status": "error"},
            status_code=401,
        )
    user_db = user_db[0]

    if not verify_password(user.password, user_db.password_hash):
        return JSONResponse(
            content={"message": "Invalid credentials", "status": "error"},
            status_code=401,
        )
    access_token = TokenManager.create_token({"sub": str(user_db.id), "type": "access"})

    refresh_token = TokenManager.create_token(
        {"sub": str(user_db.id), "type": "refresh"},
        TokenManager.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return Tokens(access=access_token, refresh=refresh_token)
