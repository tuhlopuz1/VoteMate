import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.core.dependencies import badresponse
from backend.models.db_adapter import adapter
from backend.models.db_tables import User

router = APIRouter()


@router.get("/get-profile-picture/{uuid}")
async def profile_picture(uuid: str):
    user = await adapter.get_by_id(User, uuid)
    if not user:
        return badresponse("Not found", 404)

    r = requests.get(user.avatar_url, stream=True)

    if r.status_code != 200:
        return badresponse("Image not accessible", r.status_code)

    return StreamingResponse(
        r.iter_content(chunk_size=8192),
        status_code=200,
        headers={
            "Content-Length": r.headers.get("Content-Length", ""),
        },
    )
