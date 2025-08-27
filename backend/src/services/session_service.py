from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from src.database.postgres.dao.dao import SessionDAO, SessionUserDAO, UserDAO
from src.services.base_service import BaseService
from src.schemas.session import SessionCreate, SessionUpdate, SessionResponse, SessionWithUsers
from src.schemas.user import UserResponse
from src.database.postgres.dao.base import connection


class SessionService(BaseService):
    """Сервис для работы с игровыми сессиями"""
    
    def __init__(self):
        super().__init__(SessionDAO)
    
    @connection
    async def create_session(self, session_data: SessionCreate, creator_id: UUID, session) -> SessionResponse:
        """
        Создание новой игровой сессии
        
        Args:
            session_data: данные сессии
            creator_id: ID создателя сессии
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            SessionResponse: созданная сессия
            
        Raises:
            ValueError: если пользователь уже участвует в другой сессии
        """
        # Проверяем, не участвует ли пользователь уже в другой сессии
        existing_session = await SessionUserDAO.find_one_by(session, user_id=creator_id)
        if existing_session:
            raise ValueError("Пользователь уже участвует в другой сессии")
        
        # Создаем сессию
        session_dict = session_data.model_dump()
        session_dict['date_start'] = datetime.now()
        
        session_obj = await self.dao.create_one(session, session_dict)
        
        # Добавляем создателя как участника с правами создателя
        await SessionUserDAO.create_one(session, {
            'session_id': session_obj.id,
            'user_id': creator_id,
            'permission': 'creator'
        })
        
        return SessionResponse.model_validate(session_obj)
    
    @connection
    async def join_session(self, session_id: UUID, user_id: UUID, permission: str = 'player', session=None) -> bool:
        """
        Присоединение пользователя к сессии
        
        Args:
            session_id: ID сессии
            user_id: ID пользователя
            permission: права пользователя (creator, moderator, player)
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            bool: True если успешно присоединился
            
        Raises:
            ValueError: если пользователь уже участвует в сессии или сессия переполнена
        """
        # Проверяем, не участвует ли пользователь уже в этой сессии
        existing_membership = await SessionUserDAO.find_one_by(
            session, user_id=user_id, session_id=session_id
        )
        if existing_membership:
            raise ValueError("Пользователь уже участвует в этой сессии")
        
        # Проверяем, не участвует ли пользователь в другой сессии
        other_session = await SessionUserDAO.find_one_by(session, user_id=user_id)
        if other_session:
            raise ValueError("Пользователь уже участвует в другой сессии")
        
        # Получаем сессию и проверяем количество участников
        session_obj = await self.get_by_id(session_id, session)
        if not session_obj:
            raise ValueError("Сессия не найдена")
        
        current_members = await SessionUserDAO.find_by(session, session_id=session_id)
        if len(current_members) >= session_obj.max_player:
            raise ValueError("Сессия переполнена")
        
        # Добавляем пользователя к сессии
        await SessionUserDAO.create_one(session, {
            'session_id': session_id,
            'user_id': user_id,
            'permission': permission
        })
        
        return True
    
    @connection
    async def leave_session(self, session_id: UUID, user_id: UUID, session=None) -> bool:
        """
        Выход пользователя из сессии
        
        Args:
            session_id: ID сессии
            user_id: ID пользователя
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            bool: True если успешно вышел
        """
        session_user = await SessionUserDAO.find_one_by(session, user_id=user_id, session_id=session_id)
        if not session_user:
            return False
        
        # Удаляем участника из сессии
        await SessionUserDAO.delete_one(session, session_user.id)
        
        # Если это был последний участник, удаляем сессию
        remaining_members = await SessionUserDAO.find_by(session, session_id=session_id)
        if not remaining_members:
            await self.delete(session_id, session)
        
        return True
    
    @connection
    async def get_session_with_users(self, session_id: UUID, session=None) -> Optional[SessionWithUsers]:
        """Получение сессии со списком участников"""
        session_obj = await self.dao.get_session_users_with_user_data(session, session_id)
        if not session_obj:
            return None
        return SessionWithUsers.model_validate(session_obj)
    
    @connection
    async def get_user_sessions(self, user_id: UUID, session=None) -> List[SessionResponse]:
        """Получение всех сессий пользователя"""
        sessions = await self.dao.find_by(session, user_id=user_id)
        return [SessionResponse.model_validate(session_obj) for session_obj in sessions]
    
    @connection
    async def update_session(self, session_id: UUID, update_data: SessionUpdate, session=None) -> Optional[SessionResponse]:
        """Обновление сессии"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict['id'] = session_id
        
        session_obj = await self.update(update_dict, session)
        if not session_obj:
            return None
        
        return SessionResponse.model_validate(session_obj)
    
    @connection
    async def end_session(self, session_id: UUID, session=None) -> bool:
        """Завершение сессии"""
        update_data = {
            'id': session_id,
            'status': 'ended',
            'date_end': datetime.now()
        }
        return await self.update(update_data, session) is not None
    
    @connection
    async def get_session_members(self, session_id: UUID, session=None) -> List[Dict[str, Any]]:
        """Получение списка участников сессии"""
        return await SessionUserDAO.get_session_users_with_user_data(session, session_id)
    
    @connection
    async def check_user_permission(self, session_id: UUID, user_id: UUID, required_permission: str, session=None) -> bool:
        """
        Проверка прав пользователя в сессии
        
        Args:
            session_id: ID сессии
            user_id: ID пользователя
            required_permission: требуемые права (creator, moderator, player)
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            bool: True если у пользователя есть требуемые права
        """
        session_user = await SessionUserDAO.find_one_by(session, user_id=user_id, session_id=session_id)
        if not session_user:
            return False
        
        # Иерархия прав: creator > moderator > player
        permission_levels = {'creator': 3, 'moderator': 2, 'player': 1}
        user_level = permission_levels.get(session_user.permission, 0)
        required_level = permission_levels.get(required_permission, 0)
        
        return user_level >= required_level
    
    @connection
    async def get_active_sessions(self, session=None) -> List[SessionResponse]:
        """Получение всех активных сессий"""
        sessions = await self.find_by({'status': 'active'}, session)
        return [SessionResponse.model_validate(session_obj) for session_obj in sessions]
    
    @connection
    async def get_session_members_count(self, session_id: UUID, session=None) -> int:
        """Получение количества участников сессии"""
        return await SessionUserDAO.count(session, session_id=session_id)
    
    @connection
    async def is_session_full(self, session_id: UUID, session=None) -> bool:
        """Проверка заполненности сессии"""
        session_obj = await self.get_by_id(session_id, session)
        if not session_obj:
            return True
        
        members_count = await self.get_session_members_count(session_id, session)
        return members_count >= session_obj.max_player 