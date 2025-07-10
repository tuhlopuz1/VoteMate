from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import UserResponse

router = APIRouter()


@router.get("/get-user-by-id/{uuid}", response_model=UserResponse)
async def get_user_by_id(uuid: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    user_db = await adapter.get_by_id(User, uuid)
    if not user_db:
        return badresponse("Not found", 404)
    user_resp = UserResponse(
        id=uuid,
        username=user_db.username,
        name=user_db.name,
        subscriptions_count=user_db.subscriptions_count,
        followers_count=user_db.followers_count,
        description=user_db.description,
        role=user_db.role,
    )
    return user_resp
