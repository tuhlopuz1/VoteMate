import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.sql import func

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
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    polls = relationship("Poll", backref="user", cascade="all, delete")
    votes = relationship("Vote", back_populates="user", cascade="all, delete")


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_username: Mapped[str] = mapped_column(String, nullable=False)
    votes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    options: Mapped[dict] = mapped_column(JSON, nullable=True)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    votes = relationship("Vote", back_populates="poll", cascade="all, delete")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    poll_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("polls.id", ondelete="CASCADE"),
        index=True,
    )
    voted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=func.now()
    )

    user = relationship("User", back_populates="votes")
    poll = relationship("Poll", back_populates="votes")

    __table_args__ = (UniqueConstraint("user_id", "poll_id", name="uq_vote_user_poll"),)
