import uuid

from sqlalchemy import Enum, String, Text, Uuid
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from backend.core.config import DEFAULT_AVATAR_URL
from backend.models.schemas import Role

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    avatar_url: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_AVATAR_URL)
