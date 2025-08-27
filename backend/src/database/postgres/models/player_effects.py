from typing import Optional
from uuid import UUID
from sqlalchemy import ForeignKey, JSON, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.database.postgres.sql_enums import EffectType, EffectCategory


class PlayerEffects(Base):
    """
    Активные эффекты игрока.
    Хранит все пассивные и активные эффекты, которые влияют на игрока.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("players.id"), index=True)
    item_instance_id: Mapped[Optional[int]] = mapped_column(ForeignKey("item_instances.id"), nullable=True, index=True)
    
    # Информация об эффекте
    effect_name: Mapped[str] = mapped_column(String(100))  # Название эффекта
    effect_type: Mapped[EffectType]  # Тип эффекта
    effect_category: Mapped[EffectCategory]  # Категория эффекта
    
    # Параметры эффекта
    turns_remaining: Mapped[int] = mapped_column(Integer, default=0)  # Сколько ходов осталось
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Активен ли эффект
    
    # Дополнительные параметры в JSON
    effect_data: Mapped[dict] = mapped_column(JSON, default=dict)  # Дополнительные данные эффекта
    
    # Связи
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="effects",
        lazy="joined"
    )
    
    item_instance: Mapped[Optional["ItemInstance"]] = relationship(
        "ItemInstance",
        lazy="joined"
    )

    def __repr__(self):
        return f"<PlayerEffects(id={self.id}, player_id={self.player_id}, effect_name='{self.effect_name}', turns_remaining={self.turns_remaining})>" 