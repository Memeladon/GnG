from datetime import datetime
from typing import List
from uuid import UUID
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Session(Base):
    """Игровая сессия."""

    id: Mapped[UUID] = mapped_column(primary_key=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_players: Mapped[int] = mapped_column(Integer)

    date_start: Mapped[datetime] = mapped_column(DateTime)
    date_end: Mapped[datetime] = mapped_column(DateTime)

    # Один-ко-Многим
    session_user: Mapped[List["SessionUser"]] = relationship(
        "SessionUser",
        back_populates="session",
        cascade="all, delete-orphan"  # Удаляет подключения к сессии при удалении сессии
    )