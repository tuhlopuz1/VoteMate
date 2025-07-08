from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User

router = APIRouter()


@router.get("/find-poll/{poll_name}")
async def find_poll(poll_name: str, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.find_similar_value(Poll, "name", poll_name)
    return poll
