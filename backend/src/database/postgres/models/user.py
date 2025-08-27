from uuid import UUID
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class User(Base):
    """Пользователь, который связывает сессию игрока с его персонажем."""

    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    mail: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Находится ли он сейчас онлайн
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связь с SessionUser (один-к-одному)
    session_user: Mapped["SessionUser"] = relationship(
        "SessionUser",
        back_populates="user",
        uselist=False
    )

    # Связь с Player (один-к-одному)
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="user",
        uselist=False
    )

