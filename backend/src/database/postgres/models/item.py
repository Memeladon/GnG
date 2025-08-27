from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text
from src.database.postgres.sql_enums import ItemType

from .base import Base


class Item(Base):
    """
    Статичный предмет, существующий в правилах игры.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    item_image: Mapped[str] = mapped_column(String(255)) # Иконка предмета
    type: Mapped[ItemType | None]
    
    uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    modifier_turns: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Связь с экземплярами предметов (один-ко-многим)
    item_instances: Mapped[List["ItemInstance"]] = relationship(
        "ItemInstance",
        back_populates="item",
        cascade="all, delete-orphan"
    )