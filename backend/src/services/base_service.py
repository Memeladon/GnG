from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from uuid import UUID

from src.database.postgres.dao.base import BaseDAO, connection

T = TypeVar('T')


class BaseService(Generic[T]):
    """Базовый сервис с общими методами для всех сервисов"""
    
    def __init__(self, dao_class: Type[BaseDAO]):
        self.dao = dao_class
    
    @connection
    async def create(self, data: Dict[str, Any], session) -> T:
        """Создание записи"""
        return await self.dao.create_one(session, data)
    
    @connection
    async def get_by_id(self, record_id: Any, session) -> Optional[T]:
        """Получение записи по ID"""
        return await self.dao.get_one(session, record_id)
    
    @connection
    async def get_all(self, session) -> List[T]:
        """Получение всех записей"""
        return await self.dao.get_all(session)
    
    @connection
    async def find_by(self, filters: Dict[str, Any], session) -> List[T]:
        """Поиск записей по произвольным полям"""
        return await self.dao.find_by(session, **filters)
    
    @connection
    async def find_one_by(self, filters: Dict[str, Any], session) -> Optional[T]:
        """Поиск одной записи по произвольным полям"""
        return await self.dao.find_one_by(session, **filters)
    
    @connection
    async def get_paginated(self, offset: int = 0, limit: int = 100, 
                           order_by: Optional[str] = None, desc_order: bool = False, session=None) -> List[T]:
        """Получение записей с пагинацией и сортировкой"""
        return await self.dao.get_paginated(session, offset, limit, order_by, desc_order)
    
    @connection
    async def update(self, data: Dict[str, Any], session) -> Optional[T]:
        """Обновление записи"""
        return await self.dao.update_one(session, data)
    
    @connection
    async def update_by(self, filters: Dict[str, Any], update_data: Dict[str, Any], session) -> int:
        """Обновление записей по произвольным полям"""
        return await self.dao.update_by(session, filters, update_data)
    
    @connection
    async def delete(self, record_id: Any, session) -> bool:
        """Удаление записи"""
        return await self.dao.delete_one(session, record_id)
    
    @connection
    async def delete_by(self, filters: Dict[str, Any], session) -> int:
        """Удаление записей по произвольным полям"""
        return await self.dao.delete_by(session, **filters)
    
    @connection
    async def exists(self, record_id: Any, session) -> bool:
        """Проверка существования записи по ID"""
        return await self.dao.exists(session, record_id)
    
    @connection
    async def exists_by(self, filters: Dict[str, Any], session) -> bool:
        """Проверка существования записи по произвольным полям"""
        return await self.dao.exists_by(session, **filters)
    
    @connection
    async def count(self, filters: Dict[str, Any] = None, session=None) -> int:
        """Подсчет количества записей с возможностью фильтрации"""
        if filters:
            return await self.dao.count(session, **filters)
        return await self.dao.count(session) 