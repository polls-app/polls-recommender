from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String, DateTime, Text, UUID,
    SmallInteger, CHAR, Enum, func
)

from core.database import Base


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(UUID, primary_key=True)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    profile_id: Mapped[str] = mapped_column(UUID)
    category_id: Mapped[str] = mapped_column(UUID)
