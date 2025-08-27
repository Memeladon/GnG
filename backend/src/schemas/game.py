from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.database.postgres.sql_enums import GameStatus

if TYPE_CHECKING:
    from .player import PlayerResponse

class GameBase(BaseModel):
    player_id: UUID
    status: GameStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    review: Optional[str] = None
    points: Optional[int] = None
    hours: Optional[float] = None

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    status: Optional[GameStatus] = None
    review: Optional[str] = None
    points: Optional[int] = None
    hours: Optional[float] = None

class GameResponse(GameBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class GameWithPlayer(GameResponse):
    player: Optional["PlayerResponse"] = None
    model_config = ConfigDict(from_attributes=True)

class GameShortInfo(BaseModel):
    id: int
    player_id: UUID
    status: GameStatus
    created_at: Optional[datetime] = None
    points: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
