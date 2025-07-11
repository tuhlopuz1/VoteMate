from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    USER = "USER"
    PRO = "PRO"


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
    refresh_token: str
    telegram_id: int
    private_key: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    name: str
    role: Role
    description: str = ""
    voted_polls: Optional[int] = 0
    created_polls: Optional[int] = 0
    notifications: bool

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
    private_key: str


class UpdateProfile(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None  # Field(
    #     default=None,
    #     min_length=3,
    #     max_length=20,
    #     pattern=r"^[a-zA-Z0-9_]+$",
    # )
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
    votes_count: int
    comments_count: int
    user_id: UUID
    user_username: str
    description: str
    options: Union[dict, list]
    start_date: datetime
    end_date: datetime
    private: bool
    is_voted: Optional[bool] = None
    is_active: bool = False
    hashtags: Optional[list] = None

    model_config = {"from_attributes": True}


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class SearchPollSchema(BaseModel):
    poll_name: Optional[str] = None
    tags: Optional[List[str]] = None
    poll_status: Optional[str] = None
    voting_status: Optional[str] = None
    sort_by: Optional[str] = None


class UserFindResponse(BaseModel):
    id: UUID
    name: str
    username: str
    similarity: Optional[int] = None
