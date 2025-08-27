from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .item_instance import ItemInstanceWithItem


class InventoryBase(BaseModel):
    """Базовая схема инвентаря"""
    player_id: int


class InventoryCreate(InventoryBase):
    """Схема для создания инвентаря"""
    pass


class InventoryUpdate(BaseModel):
    player_id: Optional[int] = None


class InventoryResponse(InventoryBase):
    """Схема для ответа с данными инвентаря"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class InventoryWithItems(InventoryResponse):
    """Схема инвентаря с предметами"""
    items: Optional[List["ItemInstanceWithItem"]] = None
    model_config = ConfigDict(from_attributes=True) 