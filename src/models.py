from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, DateTime, Text, UUID,
    SmallInteger, CHAR, Enum, func,
    Boolean, ForeignKey, Integer
)
from pgvector.sqlalchemy import Vector

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password: Mapped[str] = mapped_column(String(97))
    role: Mapped[str] = mapped_column(
        Enum("pollee", "admin", name="user_roles")
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_login: Mapped[datetime] = mapped_column(DateTime)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="user")
    polls: Mapped[list["Poll"]] = relationship("Poll", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    username: Mapped[str] = mapped_column(String(37), unique=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)
    avatar_path: Mapped[str | None] = mapped_column(String(255))
    contribution_count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"), unique=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    possible_answers_count: Mapped[int] = mapped_column(
        SmallInteger, default=1
    )
    color_hex: Mapped[str] = mapped_column(CHAR(7))
    lang_code: Mapped[str] = mapped_column(CHAR(2))
    access_mode: Mapped[str] = mapped_column(
        Enum("restricted", "public", name="poll_access_mode"),
        default="restricted"
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(830))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"))
    category_id: Mapped[str] = mapped_column(UUID)

    options: Mapped[list["Option"]] = relationship("Option", back_populates="poll")
    shares: Mapped[list["Share"]] = relationship("Share", back_populates="poll")
    user: Mapped["User"] = relationship("User", back_populates="polls")


class Option(Base):
    __tablename__ = "options"

    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(SmallInteger)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    poll_id: Mapped[str] = mapped_column(UUID, ForeignKey("polls.id"))
    
    poll: Mapped["Poll"] = relationship("Poll", back_populates="options")
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="option")


class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[str] = mapped_column(UUID, primary_key=True)
    option_id: Mapped[str] = mapped_column(UUID, ForeignKey("options.id"), primary_key=True)

    option: Mapped["Option"] = relationship("Option", back_populates="votes")


class Share(Base):
    __tablename__ = "shares"

    user_id: Mapped[str] = mapped_column(UUID, primary_key=True)
    poll_id: Mapped[str] = mapped_column(UUID, ForeignKey("polls.id"), primary_key=True)

    poll: Mapped["Poll"] = relationship("Poll", back_populates="shares")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    content: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    parent_id: Mapped[str | None] = mapped_column(UUID, ForeignKey("comments.id"))
    poll_id: Mapped[str] = mapped_column(UUID, ForeignKey("polls.id"))
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"))

    poll: Mapped["Poll"] = relationship("Poll")
    user: Mapped["User"] = relationship("User")
