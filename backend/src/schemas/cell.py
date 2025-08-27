from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class CellBase(BaseModel):
    min_time: int
    max_time: int
    effects: Optional[List[str]] = None
    traps: Optional[Dict[str, Any]] = None

class CellCreate(CellBase):
    pass

class CellUpdate(BaseModel):
    min_time: Optional[int] = None
    max_time: Optional[int] = None
    effects: Optional[List[str]] = None
    traps: Optional[Dict[str, Any]] = None

class CellPydantic(CellBase):
    id: int
    position: int
    title: str
    type: str
    background_image: str

    main_conditions: str
    genre_conditions: str | None

    model_config = ConfigDict(from_attributes=True)

