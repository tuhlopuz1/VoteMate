from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Comment, User

router = APIRouter()


@router.get("/get-comment/{comment_id}")
async def get_comment(comment_id: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)
    return {
        "id": comment.id,
        "poll_id": comment.poll_id,
        "user_id": comment.user_id,
        "user_name": comment.user_name,
        "user_username": comment.user_username,
        "parent_username": comment.parent_username,
        "content": comment.content,
        "created_at": comment.created_at,
        "replies_count": comment.replies_count,
    }
