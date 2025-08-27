from uuid import UUID
from typing import Optional, TYPE_CHECKING, List
from pydantic import BaseModel, ConfigDict
from src.database.postgres.sql_enums import UserRights

if TYPE_CHECKING:
    from .player_stats import PlayerStatsResponse
    from .user import UserResponse
    from .inventory import InventoryResponse, InventoryWithItems
    from .cell import CellPydantic
    from .player_effects import PlayerEffectsResponse
    from .game import GameResponse


class PlayerBase(BaseModel):
    """Базовая схема игрока"""
    username: str
    profile_image: str = ""
    role: UserRights
    dice_modifier: Optional[int] = None
    game_modifier: Optional[int] = None
    last_dice_value: int = 0
    previous_cell_id: int = 0


class PlayerCreate(PlayerBase):
    """Схема для создания игрока"""
    user_id: UUID
    cell_id: int
    inventory_id: int


class PlayerUpdate(BaseModel):
    """Схема для обновления игрока"""
    username: Optional[str] = None
    profile_image: Optional[str] = None
    role: Optional[UserRights] = None
    cell_id: Optional[int] = None
    dice_modifier: Optional[int] = None
    game_modifier: Optional[int] = None
    last_dice_value: Optional[int] = None
    previous_cell_id: Optional[int] = None


class PlayerResponse(PlayerBase):
    """Схема для ответа с данными игрока"""
    id: UUID
    cell_id: int
    user_id: UUID
    inventory_id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PlayerWithRelations(PlayerResponse):
    """Схема игрока с связанными данными"""
    stats: Optional["PlayerStatsResponse"] = None
    user: Optional["UserResponse"] = None
    cell: Optional["CellPydantic"] = None
    inventory: Optional["InventoryResponse"] = None
    effects: Optional[List["PlayerEffectsResponse"]] = None
    game: Optional[List["GameResponse"]] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PlayerWithFullData(PlayerWithRelations):
    """Схема игрока с полными данными включая предметы"""
    inventory: Optional["InventoryWithItems"] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class InventoryPydantic(BaseModel):
    id: int
    item1: int
    item2: int
    item3: int
    item4: int
    item5: int
    item6: int

    model_config = ConfigDict(from_attributes=True)

