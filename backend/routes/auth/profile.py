from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import UserProfileResponse

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def profile(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    voted_polls = await adapter.get_by_value(Vote, "user_id", user.id)
    created_polls = await adapter.get_by_value(Poll, "user_id", user.id)
    response_user = UserProfileResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        description=user.description,
        voted_polls=len(voted_polls),
        created_polls=len(created_polls),
        notifications=user.notifications,
    )

    return response_user
