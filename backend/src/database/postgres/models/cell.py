from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, JSON

from .base import Base
from src.database.postgres.sql_enums import CellType, GameConditions


class Cell(Base):
    """Ячейка на игровом поле."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(String(100))
    type: Mapped[CellType]
    background_image: Mapped[str] = mapped_column(String(255))

    # Условия для колеса игр. Игрок выбирает ЛИБО основные, ЛИБО жанровое (дополнительное)
    main_conditions: Mapped[str] = mapped_column(Text)
    genre_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ловушки на клетке: {"название_ловушки": {"created_by": "player_id", "uses_remaining": int, "data": dict}}
    traps: Mapped[dict] = mapped_column(JSON, default=dict)

    # Связывает выпавшую игру с ячейкой, на которой она выпала
    # Один-ко-Многим
    game: Mapped[List["Game"]] = relationship(
        "Game",
        back_populates="cell",
        cascade="all, delete-orphan"
    )

    # Связь с игроками на этой клетке (один-ко-многим)
    players: Mapped[List["Player"]] = relationship(
        "Player",
        back_populates="cell",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Cell(id={self.id}, title='{self.title}', type='{self.type}')>"

