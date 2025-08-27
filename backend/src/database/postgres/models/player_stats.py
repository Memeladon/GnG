from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID

from .base import Base

class PlayerStats(Base):
    """
    PlayerStats — статистика игрока за все время.
    Хранит счетчики побед, сыгранных раундов, использованных предметов и т.д.
    Один-к-одному с Player.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("players.id"), unique=True, index=True)
    win_points: Mapped[int] = mapped_column(default=0, doc="Победные очки")
    round_count: Mapped[int] = mapped_column(default=0, doc="Пройдено кругов")

    total_games: Mapped[int] = mapped_column(default=0, doc="Всего игр")
    count_completed_games: Mapped[int] = mapped_column(default=0, doc="Пройдено игр")
    count_rerolled_games: Mapped[int] = mapped_column(default=0, doc="Рероллов игр")
    count_dropped_games: Mapped[int] = mapped_column(default=0, doc="Дропнуто игр")
    count_used_items: Mapped[int] = mapped_column(default=0, doc="Использовано предметов")

    average_dice_value: Mapped[float] = mapped_column(default=0, doc="Среднее значение кубика")

    player: Mapped["Player"] = relationship("Player", back_populates="stats", uselist=False) 