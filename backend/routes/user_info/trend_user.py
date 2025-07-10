from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.schemas import UserFindResponse

router = APIRouter()


@router.get("/trend-user")
async def get_trend_user(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    all_polls = await adapter.get_all(Poll)
    data = {}
    for i in all_polls:
        data[i.user_id] = data.get(i.user_id, 0) + i.votes_count
    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    data = data[:20]
    res = []
    for i in data:
        res.append(
            UserFindResponse.model_validate(
                await adapter.get_by_id(User, i[0]), from_attributes=True
            )
        )
    return res
