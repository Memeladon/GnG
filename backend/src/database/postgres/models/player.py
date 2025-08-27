from typing import List
from uuid import UUID
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.database.postgres.sql_enums import UserRights


class Player(Base):
    """
    Игровой персонаж пользователя.
    Содержит только актуальные игровые данные, статистика вынесена в PlayerStats.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True)
    cell_id: Mapped[int] = mapped_column(ForeignKey("cells.id"), index=True) # Позиция на игровом поле
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

    # Информация об игроке
    username: Mapped[str] = mapped_column(unique=True)
    profile_image: Mapped[str] = mapped_column(default="")

    # Админ/Модератор/Игрок
    role: Mapped[UserRights]

    # Игровые данные
    last_dice_value: Mapped[int] = mapped_column(default=0) # Значение последнего броска кубика
    previous_cell_id: Mapped[int] = mapped_column(default=0) # Предыдущая позиция (для туалетки)
    
    # Статистика игрока (один-к-одному)
    stats: Mapped["PlayerStats"] = relationship(
        "PlayerStats",
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Связь с пользователем (один-к-одному)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="player",
        uselist=False,
        lazy="joined"
    )

    # Связь с клеткой (один-к-одному)
    cell: Mapped["Cell"] = relationship(
        "Cell",
        back_populates="players",
        uselist=False
    )

    # Связь с инвентарем (один-к-одному)
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )

    # Связь с эффектами (один-ко-многим)
    effects: Mapped[List["PlayerEffects"]] = relationship(
        "PlayerEffects",
        back_populates="player",
        cascade="all, delete-orphan"
    )

    # Связь с играми (один-ко-многим)
    game: Mapped[List["Game"]] = relationship(
        "Game",
        back_populates="player",
        cascade="all, delete-orphan"
    )

