from datetime import datetime
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .user import UserResponse


class SessionBase(BaseModel):
    """Базовая схема сессии"""
    status: Optional[str] = None
    max_player: int


class SessionCreate(SessionBase):
    """Схема для создания сессии"""
    pass


class SessionUpdate(BaseModel):
    """Схема для обновления сессии"""
    status: Optional[str] = None
    max_player: Optional[int] = None


class SessionResponse(SessionBase):
    """Схема для ответа с данными сессии"""
    id: UUID
    date_start: datetime
    date_end: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SessionWithUsers(SessionResponse):
    """Схема сессии с пользователями"""
    session_users: List["SessionUserResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class SessionUserBase(BaseModel):
    """Базовая схема пользователя сессии"""
    permission: str


class SessionUserCreate(SessionUserBase):
    """Схема для создания пользователя сессии"""
    session_id: UUID
    user_id: UUID


class SessionUserUpdate(BaseModel):
    """Схема для обновления пользователя сессии"""
    permission: Optional[str] = None


class SessionUserResponse(SessionUserBase):
    """Схема для ответа с данными пользователя сессии"""
    id: int
    session_id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class SessionUserWithUser(SessionUserResponse):
    """Схема пользователя сессии с данными пользователя"""
    user: "UserResponse"

    model_config = ConfigDict(from_attributes=True)
