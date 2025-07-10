import io
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from PIL import Image

from backend.core.config import DEFAULT_AVATAR_URL
from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.s3_adapter import s3

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def center_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    return image.crop((left, top, right, bottom))


@router.put("/profile-picture")
async def updt_pfp(
    user: Annotated[User, Depends(check_user)],
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        return badresponse("Unsupported file", 415)
    if not user:
        return badresponse("Unauthorized", 401)

    filename = f"{user.username}/avatar_{user.id}.png"
    img = Image.open(file.file).convert("RGB")
    img = center_crop(img)
    img = img.resize((512, 512))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = buffer.getvalue()

    if user.avatar_url != DEFAULT_AVATAR_URL:
        try:
            await s3.delete_file(filename)
        except Exception as e:
            logger.error(f"Failed to remove old avatar: {e}")
            return badresponse(f"Failed to remove old avatar: {e}", 500)

    try:
        await s3.upload_file(data, filename)
        public_url = s3.get_url(filename)
        await adapter.update_by_id(User, user.id, {"avatar_url": public_url})
        return okresp(200, "Updated")
    except Exception as e:
        logger.error(f"Failed to upload avatar: {e}")
        return badresponse(f"Failed to upload avatar: {e}", 500)


@router.delete("/profile-picture", status_code=204)
async def del_pfp(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    if not user.avatar_url:
        return badresponse("Not found", 404)

    filename = f"{user.username}/avatar_{user.id}.png"
    try:
        await s3.delete_file(filename)
        await adapter.update_by_id(User, user.id, {"avatar_url": DEFAULT_AVATAR_URL})
        return okresp(204)
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        return badresponse(f"Error deleting old avatar: {e}", 500)
