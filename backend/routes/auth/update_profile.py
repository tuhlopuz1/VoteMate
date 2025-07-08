import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from supabase import AsyncClient, create_async_client

from backend.core.config import DEFAULT_AVATAR_URL, SUPABASE_API, SUPABASE_URL
from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import UpdateProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
supabase: AsyncClient | None = None


async def get_supabase_client() -> AsyncClient:
    global supabase
    if supabase is None:
        supabase = await create_async_client(SUPABASE_URL, SUPABASE_API)
    return supabase


@router.put("/update-profile")
async def upd_profile(user: Annotated[User, Depends(check_user)], update: UpdateProfile):
    if not user:
        return badresponse("Unauthorized", 401)

    updated_data = {}
    uid = user.id

    if update.name:
        updated_data["name"] = update.name

    if update.username:
        update.username = f"@{update.username}"
        existing_username = await adapter.get_by_value(User, "username", update.username)
        if not existing_username:
            updated_data["username"] = update.username
            if user.avatar_url != DEFAULT_AVATAR_URL:
                supabase = await get_supabase_client()
                old_pfp = f"{user.username}/avatar_{uid}.png"
                new_pfp = f"{update.username}/avatar_{uid}.png"
                try:
                    await supabase.storage.from_("pfps").copy(old_pfp, new_pfp)
                    await supabase.storage.from_("pfps").remove([old_pfp])
                    public_url = await supabase.storage.from_("pfps").get_public_url(new_pfp)
                    await adapter.update_by_id(User, uid, {"avatar_url": public_url})
                except Exception as e:
                    logger.error(f"Ошибка при перемещении аватара: {e}")
        else:
            return badresponse("This username is already taken", 409)

    if update.description:
        updated_data["description"] = update.description

    if not updated_data:
        return badresponse("No fields provided")

    await adapter.update_by_id(User, uid, updated_data)
    return okresp(message="Profile updated successfully")
