from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import UserResponse

router = APIRouter()


@router.get("/get-user/{username}", response_model=UserResponse)
async def get_user(username: str, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    if not username.startswith("@"):
        username = f"@{username}"
    user = await adapter.get_by_value(User, "username", username)
    if not user:
        return badresponse("User not found", 404)
    user = user[0]
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        description=user.description,
        role=user.role,
    )
    return user_resp
