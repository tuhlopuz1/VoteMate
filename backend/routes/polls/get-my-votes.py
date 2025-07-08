from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/get-my-votes")
async def get_my_votes(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    user_polls = await adapter.get_polls_voted_by_user(user.id)
    polls_sch = []
    for poll in user_polls:
        poll_sch = PollSchema.model_validate(poll)
        poll_sch.is_voted = True
        if poll.end_date > datetime.utcnow():
            poll_sch.options = None
    return polls_sch
