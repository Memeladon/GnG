from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID

from .base import Base


class Inventory(Base):
    """
    Инвентарь игрока. Хранит связь с игроком и список предметов (ItemInstance).
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Связь с игроком (один-к-одному)
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="inventory",
        uselist=False,
        single_parent=True
    )

    # Связь с экземплярами предметов (один-ко-многим)
    items: Mapped[list["ItemInstance"]] = relationship(
        "ItemInstance",
        back_populates="inventory",
        cascade="all, delete-orphan"
    )