from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Comment, Poll, User

router = APIRouter()


@router.post("/add-comment/{poll_id}")
async def add_comment(
    user: Annotated[User, Depends(check_user)],
    poll_id: UUID,
    parent_id: UUID | None = None,
    content: str = Body(...),
):
    if not user:
        return badresponse("Unauthorized", 401)
    if len(content) < 2:
        return badresponse("Comment too short")
    poll = await adapter.get_by_id(Poll, poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    parent_comment = await adapter.get_by_id(Comment, parent_id)
    if parent_comment:
        parent_username = parent_comment.user_username
        await adapter.update_by_id(
            Comment,
            parent_id,
            {"replies_count": parent_comment.replies_count + 1},
        )
    else:
        parent_username = None
    new_comment = {
        "poll_id": poll_id,
        "user_id": user.id,
        "user_name": user.name,
        "user_username": user.username,
        "parent_id": parent_id,
        "parent_username": parent_username,
        "content": content,
    }
    await adapter.update_by_id(Poll, poll_id, {"comments": poll.comments + 1})
    new_comm = await adapter.insert(Comment, new_comment)
    return okresp(201, str(new_comm.id))
