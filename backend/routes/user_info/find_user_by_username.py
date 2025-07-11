from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import UserFindResponse

router = APIRouter()


@router.get("/find-user-by-username")
async def find_user(username: str, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    res = await adapter.find_similar_value(User, "username", f"{username}")
    users = []
    for user in res:
        user_model = UserFindResponse(
            id=user["id"],
            name=user["name"],
            username=user["username"],
            similarity=user["similarity"],
        )
        users.append(user_model)
    users.sort(key=lambda x: x.similarity, reverse=True)
    return users
