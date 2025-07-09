from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User

router = APIRouter()


@router.get("/trend-poll")
async def get_trend_poll(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    all_polls = await adapter.get_all(Poll)
    all_polls.sort(key=lambda x: x.votes_count, reverse=True)
    return all_polls[:20]
