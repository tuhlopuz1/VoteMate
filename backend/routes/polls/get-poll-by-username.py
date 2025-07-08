from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/get-poll-by-user/{username}")
async def get_poll_by_user_id(username: str, user: Annotated[User, Depends(check_user)]):
    if not username.startswith("@") and user:
        username = "@" + username
    polls = await adapter.get_by_value(Poll, "user_username", username)
    if user and user.username == username:
        return polls
    polls_user = []
    for poll in polls:
        if not poll.private:
            if poll.end_date <= datetime.utcnow():
                poll_dict = PollSchema.model_validate(poll).model_dump()
                polls_user.append(poll)
            else:
                poll_dict = PollSchema.model_validate(poll).model_dump(exclude={"options"})
                polls_user.append(poll_dict)
    return polls_user
