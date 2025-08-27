from typing import List, Any, Dict, TypeVar, Type, Optional, Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, update, delete, func, desc, asc

from src.config import settings
from src.utils.logger import log
import traceback

# ---------------------------------- CONNECTION ---------------------------------- #
POSTGRES_URL = settings.get_db_url()
if not POSTGRES_URL:
    raise ValueError("POSTGRES_URL is not defined!")

engine = create_async_engine(url=POSTGRES_URL) # Асинхронный движок для работы с БД
async_session_maker = async_sessionmaker(engine, expire_on_commit=False) # Фабрика сессий для взаимодействия с БД

def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                tb = traceback.format_exc()
                log.error(message=f"Exception in {method.__qualname__}: {e}\n{tb}")
                raise
            finally:
                await session.close()  # Закрываем сессию

    return wrapper

# ---------------------------------- ---------- ---------------------------------- #

T = TypeVar("T")

class BaseDAO:
    model: Type[T] = None  # Устанавливается в дочернем классе

    @classmethod
    async def create_one(cls, session: AsyncSession, data: dict) -> T:
        """
        Создание одной записи модели.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            data: dict - данные для создания записи
                Пример: {"name": "John", "email": "john@example.com"}
        
        Returns:
            T - созданный объект модели
        
        Raises:
            SQLAlchemyError: при ошибке создания записи
        """
        new_instance = cls.model(**data)
        session.add(new_instance)
        await session.commit()
        log.info(message=f"create_one: {cls.model.__name__} {data} -> OK id={getattr(new_instance, 'id', None)}")
        return new_instance

    @classmethod
    async def create_many(cls, session: AsyncSession, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Создание нескольких записей модели.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            data_list: List[Dict[str, Any]] - список данных для создания записей
                Пример: [
                    {"name": "John", "email": "john@example.com"},
                    {"name": "Jane", "email": "jane@example.com"}
                ]
        
        Returns:
            List[T] - список созданных объектов модели
        
        Raises:
            SQLAlchemyError: при ошибке создания записей
        """
        new_instances = [cls.model(**values) for values in data_list]
        session.add_all(new_instances)
        await session.commit()
        log.info(message=f"create_many: {cls.model.__name__} {len(data_list)} items -> OK")
        return new_instances

    @classmethod
    async def get_one(cls, session: AsyncSession, record_id: Any) -> Optional[T]:
        """
        Получение одной записи по ID.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            record_id: Any - ID записи
        
        Returns:
            Optional[T] - найденный объект модели или None
        """
        obj = await session.get(cls.model, record_id)
        log.debug(message=f"get_one: {cls.model.__name__} id={record_id} -> {'FOUND' if obj else 'NOT FOUND'}")
        return obj

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List[T]:
        """
        Получение всех записей модели.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
        
        Returns:
            List[T] - список всех объектов модели
        """
        result = await session.execute(select(cls.model))
        items = result.scalars().all()
        log.debug(message=f"get_all: {cls.model.__name__} -> {len(items)} items")
        return items

    @classmethod
    async def find_by(cls, session: AsyncSession, **filters) -> List[T]:
        """
        Поиск записей по произвольным полям.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            **filters: произвольные поля для фильтрации
                Пример: find_by(name="John", age=25)
        
        Returns:
            List[T] - список найденных объектов модели
        """
        stmt = select(cls.model).filter_by(**filters)
        result = await session.execute(stmt)
        items = result.scalars().all()
        log.debug(message=f"find_by: {cls.model.__name__} {filters} -> {len(items)} items")
        return items

    @classmethod
    async def find_one_by(cls, session: AsyncSession, **filters) -> Optional[T]:
        """
        Поиск одной записи по произвольным полям.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            **filters: произвольные поля для фильтрации
                Пример: find_one_by(name="John", email="john@example.com")
        
        Returns:
            Optional[T] - найденный объект модели или None
        """
        stmt = select(cls.model).filter_by(**filters)
        result = await session.execute(stmt)
        obj = result.scalars().first()
        log.debug(message=f"find_one_by: {cls.model.__name__} {filters} -> {'FOUND' if obj else 'NOT FOUND'}")
        return obj

    @classmethod
    async def get_paginated(cls, session: AsyncSession, offset: int = 0, limit: int = 100, 
                           order_by: Optional[str] = None, desc_order: bool = False) -> List[T]:
        """
        Получение записей с пагинацией и сортировкой.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            offset: int - смещение от начала (по умолчанию 0)
            limit: int - максимальное количество записей (по умолчанию 100)
            order_by: Optional[str] - поле для сортировки (по умолчанию None)
            desc_order: bool - сортировка по убыванию (по умолчанию False)
        
        Returns:
            List[T] - список объектов модели с пагинацией
        
        Raises:
            AttributeError: если указанное поле для сортировки не существует
        """
        stmt = select(cls.model)
        
        if order_by:
            if not hasattr(cls.model, order_by):
                log.error(message=f"get_paginated: {cls.model.__name__} order_by={order_by} -> NO SUCH FIELD")
                raise AttributeError(f"Field '{order_by}' does not exist in model {cls.model.__name__}")
            
            order_column = getattr(cls.model, order_by)
            if desc_order:
                stmt = stmt.order_by(desc(order_column))
            else:
                stmt = stmt.order_by(asc(order_column))
        
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        items = result.scalars().all()
        log.debug(message=f"get_paginated: {cls.model.__name__} offset={offset} limit={limit} -> {len(items)} items")
        return items

    @classmethod
    async def update_one(cls, session: AsyncSession, data: dict) -> Optional[T]:
        """
        Обновление одной записи по ID.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            data: dict - данные для обновления
                Пример: {"id": 1, "name": "New Name", "email": "new@example.com"}
        
        Returns:
            Optional[T] - обновленный объект модели или None если не найден
        
        Raises:
            SQLAlchemyError: при ошибке обновления записи
            ValueError: если ID не указан
        """
        record_id = data.get('id')
        obj = await session.get(cls.model, record_id)
        if not obj:
            log.warning(message=f"update_one: {cls.model.__name__} id={record_id} -> NOT FOUND")
            return None
        for k, v in data.items():
            if k != 'id':
                setattr(obj, k, v)
        await session.commit()
        log.info(message=f"update_one: {cls.model.__name__} id={record_id} -> UPDATED")
        return obj

    @classmethod
    async def update_by(cls, session: AsyncSession, filters: dict, update_data: dict) -> int:
        """
        Обновление записей по произвольным полям.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            filters: dict - условия для поиска записей
                Пример: {"status": "active"}
            update_data: dict - данные для обновления
                Пример: {"status": "inactive", "updated_at": datetime.now()}
        
        Returns:
            int - количество обновленных записей
        
        Raises:
            SQLAlchemyError: при ошибке обновления записей
        """
        stmt = update(cls.model).filter_by(**filters).values(**update_data)
        result = await session.execute(stmt)
        await session.commit()
        log.info(message=f"update_by: {cls.model.__name__} {filters} -> {result.rowcount} rows updated")
        return result.rowcount

    @classmethod
    async def delete_one(cls, session: AsyncSession, record_id: Any) -> bool:
        """
        Удаление одной записи по ID.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            record_id: Any - ID записи для удаления
        
        Returns:
            bool - True если запись удалена, False если не найдена
        
        Raises:
            SQLAlchemyError: при ошибке удаления записи
        """
        obj = await session.get(cls.model, record_id)
        if not obj:
            log.warning(message=f"delete_one: {cls.model.__name__} id={record_id} -> NOT FOUND")
            return False
        await session.delete(obj)
        await session.commit()
        log.info(message=f"delete_one: {cls.model.__name__} id={record_id} -> DELETED")
        return True

    @classmethod
    async def delete_by(cls, session: AsyncSession, **filters) -> int:
        """
        Удаление записей по произвольным полям.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            **filters: произвольные поля для фильтрации
                Пример: delete_by(status="inactive", created_at__lt=datetime.now())
        
        Returns:
            int - количество удаленных записей
        
        Raises:
            SQLAlchemyError: при ошибке удаления записей
        """
        stmt = delete(cls.model).filter_by(**filters)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

    @classmethod
    async def delete_all(cls, session: AsyncSession) -> int:
        """
        Удаление всех записей модели.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
        
        Returns:
            int - количество удаленных записей
        
        Raises:
            SQLAlchemyError: при ошибке удаления записей
        """
        result = await session.execute(delete(cls.model))
        await session.commit()
        return result.rowcount

    @classmethod
    async def count(cls, session: AsyncSession, **filters) -> int:
        """
        Подсчет количества записей модели с возможностью фильтрации.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            **filters: произвольные поля для фильтрации (по умолчанию нет фильтров)
                Пример: count(status="active")
        
        Returns:
            int - количество записей
        """
        stmt = select(func.count()).select_from(cls.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def exists(cls, session: AsyncSession, record_id: Any) -> bool:
        """
        Проверка существования записи по ID.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            record_id: Any - ID записи
        
        Returns:
            bool - True если запись существует, False иначе
        """
        instance = await session.get(cls.model, record_id)
        return instance is not None

    @classmethod
    async def exists_by(cls, session: AsyncSession, **filters) -> bool:
        """
        Проверка существования записи по произвольным полям.
        
        Args:
            session: AsyncSession - асинхронная сессия БД
            **filters: произвольные поля для фильтрации
                Пример: exists_by(name="John", email="john@example.com")
        
        Returns:
            bool - True если запись существует, False иначе
        """
        stmt = select(func.count()).select_from(cls.model).filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalar_one() > 0