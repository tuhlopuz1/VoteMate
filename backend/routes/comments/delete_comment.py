from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Comment, Poll, User

router = APIRouter()


@router.delete("/delete-comment/{comment_id}")
async def delete_comment(user: Annotated[User, Depends(check_user)], comment_id: UUID):
    if not user:
        return badresponse("Unauthorized", 401)
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)
    if comment.user_id != user.id:
        return badresponse("Forbidden", 403)
    poll = await adapter.get_by_id(Poll, comment.poll_id)
    await adapter.delete(Comment, comment_id)
    await adapter.update_by_id(Poll, comment.poll_id, {"comments": max(poll.comments - 1, 0)})
    return okresp(204)
