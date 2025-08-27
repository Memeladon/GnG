from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from uuid import UUID

from .base import Base

class SessionUser(Base):
    """Связывает сессию и пользователя."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

    # Право управления конкретной игровой сессией
    permission: Mapped[str] = mapped_column(String(50))

    # Многие-к-одному с Session
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="session_user"
    )

    # Один-к-одному
    user: Mapped["User"] = relationship(
        "User",
        back_populates="session_user",
        uselist=False,  # Ключевой параметр для связи один-к-одному
    )