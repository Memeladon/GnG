from uuid import UUID
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ItemInstance(Base):
    """
    Экземпляр предмета, находящийся в инвентаре игрока.
    """

    __tablename__ = "item_instances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventories.id"), index=True)

    # Изменяемые игроком при использовании свойства
    uses: Mapped[int] = mapped_column(Integer)
    modifier_turns: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Количество ходов действия предмета (сколько предмет еще будет действовать/быть активным)

    # Связь с предметом (многие-к-одному)
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="item_instances"
    )

    # Связь с инвентарем (многие-к-одному)
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="items"
    )