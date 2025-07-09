from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.routes.polls.tasks import enqueue_notify_author

router = APIRouter()


@router.post("/end-poll/{poll_id}")
async def end_vote(poll_id: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    if poll.user_id != user.id:
        return badresponse("You are not the owner of this poll", 403)
    poll.end_date = datetime.now()
    updated_poll = {
        "end_date": poll.end_date,
        "votes_count": poll.votes_count,
        "options": poll.options,
        "user_id": poll.user_id,
        "user_username": poll.user_username,
        "name": poll.name,
        "description": poll.description,
        "start_date": poll.start_date,
        "private": poll.private,
        "id": poll.id,
    }
    await adapter.update(Poll, updated_poll, poll_id)
    await enqueue_notify_author(user.telegram_id, poll_id, 0.0)
    return okresp(200, "Poll ended")
