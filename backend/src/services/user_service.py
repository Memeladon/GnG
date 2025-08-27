import secrets
from typing import Optional, Dict, Any
from uuid import UUID

from src.database.postgres.dao.dao import UserDAO
from src.services.base_service import BaseService
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserAuthResponse
from src.database.postgres.dao.base import connection
from src.crypto.crypto import pwd_context, create_access_token, verify, get_current_user


class UserService(BaseService):
    """
    Сервис для работы с пользователями
    """
    def __init__(self):
        super().__init__(UserDAO)
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля с использованием scrypt"""
        return pwd_context.hash(password)
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return verify(password, hashed_password)
    
    def create_access_token(self, username: str) -> str:
        """Создание JWT токена для пользователя"""
        return create_access_token({"username": username})
    
    @connection
    async def register_user(self, user_data: UserCreate, session) -> UserResponse:
        """
        Регистрация нового пользователя
        
        Args:
            user_data: данные пользователя для регистрации
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            UserResponse: созданный пользователь
            
        Raises:
            ValueError: если пользователь с таким логином уже существует
        """
        # Проверяем, не существует ли уже пользователь с таким логином
        existing_user = await self.dao.find_one_by(session, login=user_data.login)
        if existing_user:
            raise ValueError(f"Пользователь с логином '{user_data.login}' уже существует")
        
        # Хешируем пароль с использованием scrypt
        hashed_password = self._hash_password(user_data.password)
        
        # Создаем пользователя
        user_dict = user_data.model_dump()
        user_dict['password'] = hashed_password
        
        user = await self.dao.create_user_unique(session, user_dict)
        return UserResponse.model_validate(user)
    
    @connection
    async def authenticate_user(self, login: str, password: str, session) -> Optional[UserAuthResponse]:
        """
        Аутентификация пользователя с возвратом токена
        
        Args:
            login: логин пользователя
            password: пароль пользователя
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            UserAuthResponse: данные пользователя и токен если аутентификация успешна, None иначе
        """
        user = await self.dao.find_one_by(session, login=login)
        if not user:
            return None
        
        # Проверяем пароль с использованием scrypt
        if not self._verify_password(password, user.password):
            return None
        
        # Проверяем, что пользователь активен
        if not user.is_active:
            return None
        
        # Создаем токен доступа
        access_token = self.create_access_token(user.login)
        
        return UserAuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            token_type="bearer"
        )
    
    @connection
    async def authenticate_user_simple(self, login: str, password: str, session) -> Optional[UserResponse]:
        """
        Простая аутентификация пользователя (без токена)
        
        Args:
            login: логин пользователя
            password: пароль пользователя
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            UserResponse: пользователь если аутентификация успешна, None иначе
        """
        user = await self.dao.find_one_by(session, login=login)
        if not user:
            return None
        
        # Проверяем пароль с использованием scrypt
        if not self._verify_password(password, user.password):
            return None
        
        # Проверяем, что пользователь активен
        if not user.is_active:
            return None
        
        return UserResponse.model_validate(user)
    
    @connection
    async def get_user_by_login(self, login: str, session) -> Optional[UserResponse]:
        """Получение пользователя по логину"""
        user = await self.dao.find_one_by(session, login=login)
        if not user:
            return None
        return UserResponse.model_validate(user)
    
    @connection
    async def update_user_profile(self, user_id: UUID, update_data: UserUpdate, session) -> Optional[UserResponse]:
        """
        Обновление профиля пользователя
        
        Args:
            user_id: ID пользователя
            update_data: данные для обновления
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            UserResponse: обновленный пользователь
        """
        # Если обновляется пароль, хешируем его с использованием scrypt
        if update_data.password:
            update_data.password = self._hash_password(update_data.password)
        
        # Убираем None значения
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict['user_id'] = user_id
        
        user = await self.dao.update_one(session, update_dict)
        if not user:
            return None
        
        return UserResponse.model_validate(user)
    
    @connection
    async def change_password(self, user_id: UUID, old_password: str, new_password: str, session) -> bool:
        """
        Изменение пароля пользователя
        
        Args:
            user_id: ID пользователя
            old_password: старый пароль
            new_password: новый пароль
            session: сессия базы данных
            
        Returns:
            bool: True если пароль изменен успешно
        """
        user = await self.dao.get_by_id(session, user_id)
        if not user:
            return False
        
        # Проверяем старый пароль
        if not self._verify_password(old_password, user.password):
            return False
        
        # Хешируем новый пароль
        hashed_new_password = self._hash_password(new_password)
        
        # Обновляем пароль
        update_dict = {'user_id': user_id, 'password': hashed_new_password}
        updated_user = await self.dao.update_one(session, update_dict)
        
        return updated_user is not None
    
    @connection
    async def deactivate_user(self, user_id: UUID, session) -> bool:
        """Деактивация пользователя"""
        update_data = {'id': user_id, 'is_active': False}
        return await self.update(session, update_data) is not None
    
    @connection
    async def activate_user(self, user_id: UUID, session) -> bool:
        """Активация пользователя"""
        update_data = {'id': user_id, 'is_active': True}
        return await self.update(session, update_data) is not None
    
    @connection
    async def get_user_with_relations(self, user_id: UUID, session) -> Optional[Dict[str, Any]]:
        """Получение пользователя со всеми связанными данными"""
        user = await self.dao.get_one(session, user_id)
        if not user:
            return None
        return user
    
    @connection
    async def get_user_by_token(self, token: str, session) -> Optional[UserResponse]:
        """
        Получение пользователя по JWT токену
        
        Args:
            token: JWT токен
            session: сессия базы данных
            
        Returns:
            UserResponse: пользователь если токен валиден, None иначе
        """
        try:
            # Используем функцию из crypto.py для валидации токена
            token_data = get_current_user(token)
            username = token_data.get("username")
            
            if not username:
                return None
            
            # Получаем пользователя по логину
            user = await self.dao.find_one_by(session, login=username)
            if not user or not user.is_active:
                return None
            
            return UserResponse.model_validate(user)
        except Exception:
            return None 