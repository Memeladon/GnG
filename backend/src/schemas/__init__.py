from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ServiceResult(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None

# User schemas
from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserWithRelations
)

# Player schemas
from .player import (
    PlayerBase, PlayerCreate, PlayerUpdate, PlayerResponse, 
    PlayerWithRelations, PlayerWithFullData
)

# PlayerStats schemas
from .player_stats import (
    PlayerStatsBase, PlayerStatsCreate, PlayerStatsUpdate, PlayerStatsResponse
)

# Inventory schemas
from .inventory import (
    InventoryBase, InventoryCreate, InventoryResponse, InventoryWithItems
)

# Item schemas
from .item import (
    ItemBase, ItemCreate, ItemUpdate, ItemResponse, ItemWithInstances
)

# ItemInstance schemas
from .item_instance import (
    ItemInstanceBase, ItemInstanceCreate, ItemInstanceUpdate, 
    ItemInstanceResponse, ItemInstanceWithItem
)

# Session schemas
from .session import (
    SessionBase, SessionCreate, SessionUpdate, SessionResponse, SessionWithUsers,
    SessionUserBase, SessionUserCreate, SessionUserUpdate, 
    SessionUserResponse, SessionUserWithUser
)

# Cell schemas
from .cell import CellPydantic

# Game schemas
from .game import GamePydantic
