from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/get-polls-by-username/{username}")
async def get_poll_by_user_id(username: str, user: Annotated[User, Depends(check_user)]):
    if not username.startswith("@"):
        username = "@" + username
    polls = await adapter.get_by_value(Poll, "user_username", username)
    if user and user.username == username:
        return polls
    polls_user = []
    for poll in polls:
        poll_sch = PollSchema.model_validate(poll)
        if user:
            vote = await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll.id})
            if vote:
                poll_sch.is_voted = True
                if poll.end_date > datetime.utcnow():
                    poll_sch.options = None
                polls_user.append(poll_sch)
                continue
        if poll.end_date > datetime.utcnow():
            poll_sch.options = None
        if not poll.private:
            polls_user.append(poll_sch)
    return polls_user
