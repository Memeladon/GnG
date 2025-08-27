from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .item import ItemResponse
    from .inventory import InventoryResponse


class ItemInstanceBase(BaseModel):
    """Базовая схема экземпляра предмета"""
    uses: int
    modifier_turns: Optional[int] = None


class ItemInstanceCreate(ItemInstanceBase):
    """Схема для создания экземпляра предмета"""
    item_id: int
    inventory_id: int


class ItemInstanceUpdate(BaseModel):
    """Схема для обновления экземпляра предмета"""
    uses: Optional[int] = None
    modifier_turns: Optional[int] = None


class ItemInstanceResponse(ItemInstanceBase):
    """Схема для ответа с данными экземпляра предмета"""
    id: int
    item_id: int
    inventory_id: int

    model_config = ConfigDict(from_attributes=True)


class ItemInstanceWithItem(ItemInstanceResponse):
    """Схема экземпляра предмета с данными предмета"""
    item: "ItemResponse"
    inventory: Optional["InventoryResponse"] = None

    model_config = ConfigDict(from_attributes=True) 