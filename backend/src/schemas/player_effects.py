from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from src.database.postgres.sql_enums import EffectType, EffectCategory

class PlayerEffectsBase(BaseModel):
    effect_name: str
    effect_type: EffectType
    effect_category: EffectCategory
    turns_remaining: Optional[int] = 0
    is_active: bool = True
    effect_data: Optional[Dict[str, Any]] = None

class PlayerEffectsCreate(PlayerEffectsBase):
    player_id: UUID
    item_instance_id: Optional[int] = None

class PlayerEffectsUpdate(BaseModel):
    turns_remaining: Optional[int] = None
    is_active: Optional[bool] = None
    effect_data: Optional[Dict[str, Any]] = None

class PlayerEffectsResponse(PlayerEffectsBase):
    id: int
    player_id: UUID
    item_instance_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True) 