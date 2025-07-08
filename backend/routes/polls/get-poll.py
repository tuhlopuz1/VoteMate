import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User

router = APIRouter()


@router.get("/get-poll/{poll_id}")
async def get_poll_by_id(poll_id: uuid.UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, id=poll_id)
    return poll
