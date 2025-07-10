from typing import Annotated

from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import PasswordUpdate

router = APIRouter()


@router.put("/change-password")
async def change_password(passwords: PasswordUpdate, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    if passwords.old_password == passwords.new_password:
        return badresponse("New password must be different from old password", 400)
    if len(passwords.new_password) < 6 or len(passwords.new_password) > 32:
        return badresponse("Invalid lenght of password", 400)
    if checkpw(passwords.old_password.encode(), user.hashed_password.encode()):
        passwords.new_password = hashpw(passwords.new_password.encode(), gensalt(5)).decode()
        await adapter.update_by_id(User, user.id, {"hashed_password": passwords.new_password})
        return okresp(200, "Password changed")
    return badresponse("Old password is incorrect!", 400)
