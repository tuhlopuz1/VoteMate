from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import FilterPollSchema

router = APIRouter()


async def check_poll_status(data, poll_status):
    if poll_status in ["all", None]:
        return True
    if poll_status == "open" and data.start_date <= datetime.now(timezone.utc) <= data.end_date:
        return True
    if poll_status == "closed" and data.end_date <= datetime.now(timezone.utc):
        return True
    return False


async def check_vote_status(data, vote_status, user_id):
    if vote_status in ["all", None]:
        return True
    vote = await adapter.get_by_value(Vote, "poll_id", data.id)
    if user_id in [i.user_id for i in vote]:
        check_vote = True
    else:
        check_vote = False
    if vote_status == "voted" and check_vote:
        return True
    if vote_status == "not_voted" and not check_vote:
        return True
    return False


@router.post("/filter-poll")
async def filter_polls(
    user: Annotated[User, Depends(check_user)],
    filters: FilterPollSchema,
):
    if not user:
        return badresponse("Unauthorized", 401)
    if filters.voting_status not in ["all", "voted", "not_voted", None]:
        return badresponse("Invalid votung status", 400)
    if filters.sort_by not in ["popularity_asc", "popularity_desc", None]:
        return badresponse("Invalid sorting", 400)
    if filters.poll_status not in ["all", "open", "closed", None]:
        return badresponse("Invalid poll status", 400)
    all_polls = await adapter.get_all(Poll)
    res = []
    for i in all_polls:
        if await check_poll_status(i, filters.poll_status):
            if await check_vote_status(i, filters.voting_status, user.id):
                if i.hashtags is not None and (
                    filters.tags is None or set(filters.tags).issubset(i.hashtags)
                ):
                    res.append(i)
    if filters.sort_by == "popularity_asc":
        res.sort(key=lambda x: x.votes_count)
    if filters.sort_by == "popularity_desc":
        res.sort(key=lambda x: x.votes_count, reverse=True)
    return res
