# from typing import Annotated

# from fastapi import APIRouter, Depends

# from backend.core.dependencies import badresponse, check_user
# from backend.models.db_adapter import adapter
# from backend.models.db_tables import User

# router = APIRouter()


# @router.get("/find-user-by-name")
# async def find_user(name: str, user: Annotated[User, Depends(check_user)]):
#     if not user:
#         return badresponse("Unauthorized", 401)
#     res = await adapter.find_similar_value(User, "name", name)
#     return res
