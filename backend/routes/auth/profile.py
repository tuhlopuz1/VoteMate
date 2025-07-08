from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import check_user
from backend.models.db_tables import User
from backend.models.schemas import UserProfileResponse

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def profile(user: Annotated[User, Depends(check_user)]):

    response_user = UserProfileResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        description=user.description,
    )

    return response_user
