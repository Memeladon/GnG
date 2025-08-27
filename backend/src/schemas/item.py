from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from src.database.postgres.sql_enums import ItemType

if TYPE_CHECKING:
    from .item_instance import ItemInstanceResponse


class ItemBase(BaseModel):
    """Базовая схема предмета"""
    title: str
    description: Optional[str] = None
    type: ItemType


class ItemCreate(ItemBase):
    """Схема для создания предмета"""
    pass


class ItemUpdate(BaseModel):
    """Схема для обновления предмета"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ItemType] = None


class ItemResponse(ItemBase):
    """Схема для ответа с данными предмета"""
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemWithInstances(ItemResponse):
    """Схема предмета с экземплярами"""
    item_instances: List["ItemInstanceResponse"] = []

    model_config = ConfigDict(from_attributes=True)
