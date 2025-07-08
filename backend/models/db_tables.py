from sqlalchemy import Column, String, Uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, unique=False, nullable=False)
