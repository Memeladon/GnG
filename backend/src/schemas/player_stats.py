from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlayerStatsBase(BaseModel):
    """Базовая схема статистики игрока"""
    win_points: int = 0
    round_count: int = 0
    total_games: int = 0
    count_completed_games: int = 0
    count_rerolled_games: int = 0
    count_dropped_games: int = 0
    count_used_items: int = 0
    average_dice_value: float = 0.0


class PlayerStatsCreate(PlayerStatsBase):
    """Схема для создания статистики игрока"""
    player_id: UUID


class PlayerStatsUpdate(BaseModel):
    """Схема для обновления статистики игрока"""
    win_points: Optional[int] = None
    round_count: Optional[int] = None
    total_games: Optional[int] = None
    count_completed_games: Optional[int] = None
    count_rerolled_games: Optional[int] = None
    count_dropped_games: Optional[int] = None
    count_used_items: Optional[int] = None
    average_dice_value: Optional[float] = None


class PlayerStatsResponse(PlayerStatsBase):
    """Схема для ответа со статистикой игрока"""
    id: int
    player_id: UUID

    model_config = ConfigDict(from_attributes=True) 