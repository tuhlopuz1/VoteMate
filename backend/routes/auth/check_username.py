from fastapi import APIRouter
from pydantic import ValidationError

from backend.core.dependencies import badresponse, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import UsernameScheme

router = APIRouter()


@router.get("/check-username/{username}")
async def check_username(username: str):
    try:
        valid = UsernameScheme(username=username)
    except ValidationError:
        return badresponse("Invalid username", 400)
    if valid:
        existing_username = await adapter.get_by_value(User, "username", username)
        if existing_username:
            return badresponse("Username already exists", 409)
        return okresp()
