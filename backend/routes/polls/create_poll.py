from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.schemas import NewPoll

router = APIRouter()


@router.post("/create-poll")
async def create_poll(user: Annotated[User, Depends(check_user)], poll: NewPoll):
    if not user:
        return badresponse("Unauthorized", 401)
    options = {}
    for vote in poll.options:
        options[vote] = 0
    new_poll_obj = {
        "name": poll.name,
        "description": poll.description,
        "user_id": user.id,
        "user_username": user.username,
        "options": options,
        "start_date": poll.start_date,
        "end_date": poll.end_date,
        "private": poll.private,
    }
    new_poll_db = await adapter.insert(Poll, new_poll_obj)
    return okresp(200, message=str(new_poll_db.id))
