from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User

router = APIRouter()


@router.get("/get-poll-by-user/{username}")
async def get_poll_by_user_id(username: str, user: Annotated[User, Depends(check_user)]):
    if not username.startswith("@"):
        username = "@" + username
    polls = await adapter.get_by_value(Poll, "user_username", username)
    if user.username == username:
        return polls
    polls = [i for i in polls if i["private"] is False]
    return polls
