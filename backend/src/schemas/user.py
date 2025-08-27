from uuid import UUID
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, EmailStr

if TYPE_CHECKING:
    from .session import SessionUserResponse
    from .player import PlayerResponse


class UserBase(BaseModel):
    """Базовая схема пользователя для создания/обновления"""
    login: str
    password: str
    mail: Optional[EmailStr] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    pass


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    login: Optional[str] = None
    password: Optional[str] = None
    mail: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class UserAuthResponse(BaseModel):
    """Схема для ответа аутентификации"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class UserWithRelations(UserResponse):
    """Схема пользователя с связанными данными"""
    session_user: Optional["SessionUserResponse"] = None
    player: Optional["PlayerResponse"] = None

    model_config = ConfigDict(from_attributes=True) 