from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote

router = APIRouter()


@router.get("/get-my-votes")
async def get_my_votes(user: Annotated[User, Depends(check_user)]):
    all_votes = await adapter.get_by_value(Vote, "user_id", user.id)
    res = []
    for i in range(len(all_votes)):
        t = await adapter.get_by_id(Poll, all_votes[i].poll_id)
        res.append(t)
    return res
