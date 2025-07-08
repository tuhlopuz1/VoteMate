from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserCreate(BaseModel):
    name: str
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    password: str
    role: Optional[Role] = Role.USER
    description: str = ""


class UserRegResponse(BaseModel):
    id: UUID
    name: str
    username: str
    role: Role
    description: str = ""
    access_token: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    name: str
    role: Role
    description: str = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserLogin(BaseModel):
    identifier: str
    password: str


class Tokens(BaseModel):
    access: str
    refresh: str
