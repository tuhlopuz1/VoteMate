from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UsernameScheme(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
    )


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


class UserRegResponse(BaseModel):
    id: UUID
    name: str
    username: str
    role: Role
    access_token: str
    telegram_id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    name: str
    role: Role
    description: str = ""
    voted_polls: Optional[int] = 0
    created_polls: Optional[int] = 0

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserResponse(BaseModel):
    id: UUID
    username: str
    name: str
    description: str = ""
    role: Role

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserLogin(BaseModel):
    identifier: str
    password: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class UpdateProfile(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    description: Optional[str] = None


class NewPoll(BaseModel):
    name: str
    description: Optional[str] = ""
    start_date: datetime
    end_date: datetime
    options: list
    private: bool


class PollSchema(BaseModel):
    id: UUID
    name: str
    votes: int
    user_id: UUID
    user_username: str
    description: str
    options: Optional[dict]
    start_date: datetime
    end_date: datetime
    private: bool
    is_voted: bool = False

    model_config = {"from_attributes": True}
