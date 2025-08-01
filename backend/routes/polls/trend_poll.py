from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/trend-poll")
async def get_trend_poll(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    all_polls = await adapter.get_all(Poll)
    all_polls.sort(key=lambda x: x.votes_count, reverse=True)
    now = datetime.now(timezone.utc)
    result: list[PollSchema] = []

    for poll in all_polls:
        poll_sch = PollSchema.model_validate(poll)
        poll_sch.is_active = bool(poll_sch.start_date < now and now < poll_sch.end_date)

        if user.id == poll_sch.user_id:
            result.append(poll_sch)
            continue

        if poll_sch.options and now < poll_sch.end_date:
            poll_sch.options = list(poll_sch.options.keys())

        if user:
            vote = await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll_sch.id})
            if vote:
                poll_sch.is_voted = True
                result.append(poll_sch)
                continue

        if not poll_sch.private:
            result.append(poll_sch)

    return result[:20]
