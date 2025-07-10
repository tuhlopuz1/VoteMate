from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Comment, Poll, User

router = APIRouter()


@router.get("/get-comments/{video_id}")
async def get_comments(video_id: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    video = await adapter.get_by_id(Poll, video_id)
    if not video:
        return badresponse("Video not found", 404)
    root_comments = await adapter.get_by_values(Comment, {"video_id": video_id, "parent_id": None})
    if not root_comments:
        return []
    return root_comments
