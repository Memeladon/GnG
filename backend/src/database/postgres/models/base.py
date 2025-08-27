from sqlalchemy.orm import DeclarativeBase, declared_attr, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей"""
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    @declared_attr.directive
    def __tablename__(cls) -> str:
        if cls.__name__.lower() == "inventory":
            return "inventories"
        return cls.__name__.lower() + "s"

    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        # Получаем маппер для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}