from uuid import UUID
from sqlalchemy import ForeignKey, String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from src.database.postgres.sql_enums import GameStatus, GameConditions


class Game(Base):
    """
    Игра, которая выпадает на колесе игр.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cell_id: Mapped[int] = mapped_column(ForeignKey("cells.id"), index=True) # Позиция на игровом поле
    player_id: Mapped[UUID] = mapped_column(ForeignKey("players.id"), index=True) # Игрок, который проходит игру

    name: Mapped[str] = mapped_column(String(100)) # Название игры
    link: Mapped[str] = mapped_column(String(500)) # Ссылка на игру
    condition_type: Mapped[GameConditions] = mapped_column(default=GameConditions.MAIN)  # Выбранное условие для прохождения
    status: Mapped[GameStatus] = mapped_column(default=GameStatus.PROGRESS) # Играется/Дроп/Реролл/Пройдена
    
    # Дополнительные поля для игровой логики
    hours_played: Mapped[float | None] = mapped_column(Float, nullable=True) # Количество часов прохождения
    review_text: Mapped[str | None] = mapped_column(String(1000), nullable=True) # Отзыв игрока
    win_points: Mapped[int] = mapped_column(Integer, default=0) # Победные очки за игру
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now()) # Время создания записи
    rating: Mapped[float | None] = mapped_column(Float, nullable=True) # Оценка игры пользователем (0-10, шаг 0.5)

    # Связь с Cell (многие-к-одному)
    cell: Mapped["Cell"] = relationship(
        "Cell",
        back_populates="game"
    )

    # Связь с Player (многие-к-одному)
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="game"
    )