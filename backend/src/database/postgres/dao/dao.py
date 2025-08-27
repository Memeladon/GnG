from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from typing import List, Optional

from src.database.postgres.sql_enums import UserRights
from .base import BaseDAO
from ..models import (Cell, Game, Item, Inventory, ItemInstance, Player, PlayerStats, Session, SessionUser, User, PlayerEffects)
from src.utils.logger import log


class CellDAO(BaseDAO):
    model = Cell

    @classmethod
    async def add_trap_to_cell(cls, session: AsyncSession, cell_id: int, trap_data: dict) -> Cell:
        """
        Добавляет ловушку в JSON поле traps клетки.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            cell_id (int): ID клетки.
            trap_data (dict): Данные ловушки.
        
        Returns:
            Cell: Обновленная клетка.
        """
        cell = await cls.get_one(session, cell_id)
        if not cell:
            raise ValueError("Cell not found")
        
        traps = cell.traps or []
        traps.append(trap_data)
        
        return await cls.update_one(session, {
            "id": cell_id,
            "traps": traps
        })

    @classmethod
    async def remove_trap_from_cell(cls, session: AsyncSession, cell_id: int, trap_index: int) -> Cell:
        """
        Удаляет ловушку из JSON поля traps клетки по индексу.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            cell_id (int): ID клетки.
            trap_index (int): Индекс ловушки в массиве.
        
        Returns:
            Cell: Обновленная клетка.
        """
        cell = await cls.get_one(session, cell_id)
        if not cell:
            raise ValueError("Cell not found")
        
        traps = cell.traps or []
        if 0 <= trap_index < len(traps):
            traps.pop(trap_index)
        
        return await cls.update_one(session, {
            "id": cell_id,
            "traps": traps
        })

    @classmethod
    async def get_cell_traps(cls, session: AsyncSession, cell_id: int) -> List[dict]:
        """
        Получает список ловушек клетки.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            cell_id (int): ID клетки.
        
        Returns:
            List[dict]: Список ловушек.
        """
        cell = await cls.get_one(session, cell_id)
        if not cell:
            return []
        
        return cell.traps or []

class GameDAO(BaseDAO):
    model = Game

class ItemDAO(BaseDAO):
    model = Item

class ItemInstanceDAO(BaseDAO):
    model = ItemInstance

    @classmethod
    async def use_item(cls, session: AsyncSession, item_instance_id: int) -> Optional[ItemInstance]:
        """
        Использует экземпляр предмета (ItemInstance) из инвентаря игрока:
        - Уменьшает количество использований (uses) на 1.
        - Если uses становится 0, экземпляр удаляется из базы и из инвентаря.
        - При удалении предмета также удаляются связанные с ним эффекты.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            item_instance_id (int): Идентификатор экземпляра предмета.
        
        Returns:
            Optional[ItemInstance]: Обновленный экземпляр предмета, либо None, если экземпляр был удален.
        
        Raises:
            ValueError: Если экземпляр предмета не найден по id.
        """
        item_instance = await cls.get_one(session, item_instance_id)
        if not item_instance:
            log.error(layer='DAO', component='ItemInstanceDAO.use_item', message=f'ItemInstance {item_instance_id} not found')
            raise ValueError("Item instance not found")
        
        if item_instance.uses <= 1:
            log.info(layer='DAO', component='ItemInstanceDAO.use_item', message=f'Using last charge of ItemInstance {item_instance_id}')
            
            # При использовании последнего заряда НЕ удаляем эффекты сразу
            # Они будут удалены в конце хода через on_game_completed
            await cls.delete_one(session, item_instance_id)
            return None
        else:
            log.info(layer='DAO', component='ItemInstanceDAO.use_item', message=f'Using ItemInstance {item_instance_id}, uses left: {item_instance.uses-1}')
            return await cls.update_one(session, {
                'id': item_instance_id,
                'uses': item_instance.uses - 1
            })

class InventoryDAO(BaseDAO):
    model = Inventory

    @classmethod
    async def is_inventory_full(cls, session: AsyncSession, inventory_id: int) -> bool:
        """
        Проверяет, заполнен ли инвентарь игрока (Inventory).
        Максимальное количество предметов в инвентаре — 6.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            inventory_id (int): Идентификатор инвентаря.
        
        Returns:
            bool: True, если в инвентаре 6 и более предметов, иначе False.
        """
        count = await cls.count(session, inventory_id=inventory_id)
        full = count >= 6
        if full:
            log.warning(layer='DAO', component='InventoryDAO.is_inventory_full', message=f'Inventory {inventory_id} is full ({count} items)')
        return full

    @classmethod
    async def add_item_to_inventory(cls, session: AsyncSession, data: dict) -> ItemInstance:
        """
        Добавляет новый экземпляр предмета (ItemInstance) в инвентарь игрока.
        Проверяет, что инвентарь не заполнен.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для создания экземпляра предмета. Ожидаемые ключи:
                - inventory_id (int): ID инвентаря
                - item_id (int): ID предмета
                - uses (int): Количество использований
                - modifier_turns (int | None): Количество ходов действия модификатора (опционально)
        
        Returns:
            ItemInstance: Созданный экземпляр предмета.
        
        Raises:
            ValueError: Если инвентарь заполнен (6 предметов).
        """
        if await cls.is_inventory_full(session, data["inventory_id"]):
            log.error(layer='DAO', component='InventoryDAO.add_item_to_inventory', message=f'Inventory {data["inventory_id"]} is full, cannot add item')
            raise ValueError("Inventory is full (max 6 items)")
        
        log.info(layer='DAO', component='InventoryDAO.add_item_to_inventory', message=f'Adding item {data["item_id"]} to inventory {data["inventory_id"]}')
        return await ItemInstanceDAO.create_one(session, data)

    @classmethod
    async def replace_item_in_inventory(cls, session: AsyncSession, data: dict) -> ItemInstance:
        """
        Заменяет существующий экземпляр предмета (ItemInstance) в инвентаре на новый.
        Старый экземпляр удаляется, новый создается с заданными параметрами.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для замены. Ожидаемые ключи:
                - inventory_id (int): ID инвентаря
                - old_item_instance_id (int): ID удаляемого экземпляра
                - new_item_id (int, optional): ID нового предмета (если не указан, используется старый)
                - new_uses (int): Количество использований нового экземпляра
                - new_modifier_turns (int, optional): Количество ходов действия модификатора
        
        Returns:
            ItemInstance: Новый экземпляр предмета.
        
        Raises:
            ValueError: Если старый экземпляр не найден в инвентаре.
        """
        old_item = await ItemInstanceDAO.get_one(session, data["old_item_instance_id"])
        if not old_item or old_item.inventory_id != data["inventory_id"]:
            log.error(layer='DAO', component='InventoryDAO.replace_item_in_inventory', message=f'ItemInstance {data["old_item_instance_id"]} not found in inventory {data["inventory_id"]}')
            raise ValueError("Item instance not found in this inventory")
        
        log.info(layer='DAO', component='InventoryDAO.replace_item_in_inventory', message=f'Replacing ItemInstance {data["old_item_instance_id"]} in inventory {data["inventory_id"]}')
        await ItemInstanceDAO.delete_one(session, data["old_item_instance_id"])
        
        new_item_data = {
            "item_id": data.get("new_item_id", old_item.item_id),
            "inventory_id": data["inventory_id"],
            "uses": data["new_uses"],
            "modifier_turns": data.get("new_modifier_turns")
        }
        
        return await ItemInstanceDAO.create_one(session, new_item_data)

    @classmethod
    async def search_items_in_inventory(
        cls, session: AsyncSession, inventory_id: int, item_name: str = None
    ) -> List[ItemInstance]:
        """
        Ищет экземпляры предметов (ItemInstance) в инвентаре игрока по названию предмета (Item.title).
        Если название не указано, возвращает все предметы в инвентаре.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            inventory_id (int): Идентификатор инвентаря.
            item_name (str, optional): Название предмета для поиска (поиск по подстроке, регистронезависимо).
        
        Returns:
            List[ItemInstance]: Список найденных экземпляров предметов.
        """
        query = select(ItemInstance).where(ItemInstance.inventory_id == inventory_id)
        if item_name:
            query = query.join(Item).where(Item.title.ilike(f"%{item_name}%"))
        
        result = await session.execute(query)
        return result.scalars().all()

class PlayerDAO(BaseDAO):
    model = Player

    @classmethod
    async def create_player_first_time(cls, session: AsyncSession, data: dict) -> Player:
        """
        Создает нового игрового персонажа (Player) для пользователя, а также инвентарь (Inventory) и статистику (PlayerStats).
        Проверяет, что у пользователя еще нет персонажа.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для создания игрока. Ожидаемые ключи:
                - user_id (UUID): ID пользователя
                - username (str): Имя игрока (уникальное)
                - profile_image (str, optional): Аватар игрока
        
        Returns:
            Player: Созданный объект игрока.
        
        Raises:
            ValueError: Если у пользователя уже есть персонаж.
        """
        if await cls.exists_by(session, user_id=data["user_id"]):
            log.error(layer='DAO', component='PlayerDAO.create_player_first_time', message=f'User {data["user_id"]} already has a Player')
            raise ValueError("User already has a Player")
        
        log.info(layer='DAO', component='PlayerDAO.create_player_first_time', message=f'Creating Player for user {data["user_id"]}')
        
        # Создать Inventory
        inventory = Inventory()
        session.add(inventory)
        await session.flush()
        
        # Создать Player
        player = cls.model(
            id=uuid4(),
            cell_id=0,
            user_id=data["user_id"],
            username=data["username"],
            profile_image=data.get("profile_image", ""),
            inventory_id=inventory.id,
            role=UserRights.PLAYER,
            last_dice_value=0,
            previous_cell_id=0
        )
        session.add(player)
        await session.flush()
        
        # Привязать inventory к player
        inventory.player_id = player.id
        
        # Создать PlayerStats
        stats = PlayerStats(player_id=player.id)
        session.add(stats)
        await session.commit()
        return player

    @classmethod
    async def update_player_profile(cls, session: AsyncSession, data: dict) -> Player:
        """
        Обновляет профиль игрока (Player): имя пользователя и аватар.
        Проверяет уникальность имени пользователя.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для обновления. Ожидаемые ключи:
                - player_id (UUID): ID игрока
                - username (str, optional): Новое имя игрока
                - profile_image (str, optional): Новый аватар
        
        Returns:
            Player: Обновленный объект игрока.
        
        Raises:
            ValueError: Если игрок не найден или имя уже занято.
        """
        player = await session.get(cls.model, data["player_id"])
        if not player:
            log.error(layer='DAO', component='PlayerDAO.update_player_profile', message=f'Player {data["player_id"]} not found')
            raise ValueError("Player not found")
        
        if "username" in data and data["username"]:
            existing_player = await cls.find_one_by(session, username=data["username"])
            if existing_player and existing_player.id != data["player_id"]:
                log.error(layer='DAO', component='PlayerDAO.update_player_profile', message=f'Username {data["username"]} already exists')
                raise ValueError("Username already exists")
        
        log.info(layer='DAO', component='PlayerDAO.update_player_profile', message=f'Updating profile for player {data["player_id"]}')
        return await cls.update_one(session, data)

    @classmethod
    async def get_players_by_session_id(cls, session: AsyncSession, session_id: UUID) -> List[Player]:
        """
        Возвращает всех игроков (Player), участвующих в игровой сессии (Session).
        Использует связь через SessionUser.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            session_id (UUID): Идентификатор игровой сессии.
        
        Returns:
            List[Player]: Список игроков, связанных с сессией.
        """
        # JOIN с SessionUser
        result = await session.execute(
            select(cls.model)
            .join(SessionUser, cls.model.user_id == SessionUser.user_id)
            .where(SessionUser.session_id == session_id)
        )
        return result.scalars().all()

class PlayerStatsDAO(BaseDAO):
    model = PlayerStats

    @classmethod
    async def increment_stats(cls, session: AsyncSession, data: dict) -> PlayerStats:
        """
        Инкрементирует (увеличивает) значения статистики игрока (PlayerStats) на указанные значения.
        Неизменяемые поля можно не указывать.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для инкремента. Ожидаемые ключи:
                - player_id (UUID): ID игрока
                - win_points (int, optional): Победные очки
                - round_count (int, optional): Пройдено кругов
                - total_games (int, optional): Всего игр
                - count_completed_games (int, optional): Пройдено игр
                - count_rerolled_games (int, optional): Рероллов игр
                - count_dropped_games (int, optional): Дропнуто игр
                - count_used_items (int, optional): Использовано предметов
                - average_dice_value (float, optional): Среднее значение кубика
        
        Returns:
            PlayerStats: Обновленный объект статистики.
        
        Raises:
            ValueError: Если статистика не найдена.
        """
        stats = await session.get(cls.model, data["player_id"])
        if not stats:
            log.error(layer='DAO', component='PlayerStatsDAO.increment_stats', message=f'PlayerStats for player {data["player_id"]} not found')
            raise ValueError("PlayerStats not found")
        
        log.info(layer='DAO', component='PlayerStatsDAO.increment_stats', message=f'Incrementing stats for player {data["player_id"]}: {data}')
        
        for field, increment in data.items():
            if field != "player_id" and hasattr(stats, field):
                current_value = getattr(stats, field) or 0
                setattr(stats, field, current_value + increment)
        
        await session.commit()
        return stats

class SessionDAO(BaseDAO):
    model = Session

    @classmethod
    async def close_session(cls, session: AsyncSession, session_id) -> Session:
        """
        Закрывает игровую сессию (Session): устанавливает date_end на текущее время.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            session_id (UUID): Идентификатор сессии.
        
        Returns:
            Session: Обновленный объект сессии.
        
        Raises:
            ValueError: Если сессия не найдена.
        """
        session_obj = await cls.get_one(session, session_id)
        if not session_obj:
            log.error(layer='DAO', component='SessionDAO.close_session', message=f'Session {session_id} not found')
            raise ValueError("Session not found")
        
        log.info(layer='DAO', component='SessionDAO.close_session', message=f'Closing session {session_id}')
        session_obj.date_end = datetime.utcnow()
        await session.commit()
        return session_obj

    @classmethod
    async def is_session_expired(cls, session: AsyncSession, session_id) -> bool:
        """
        Проверяет, истекла ли игровая сессия (Session) по дате окончания.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            session_id (UUID): Идентификатор сессии.
        
        Returns:
            bool: True, если сессия истекла или не найдена, иначе False.
        """
        session_obj = await cls.get_one(session, session_id)
        if not session_obj:
            return True
        
        if session_obj.date_end and session_obj.date_end < datetime.utcnow():
            return True
        
        return False

    @classmethod
    async def get_sessions_by_user_id(cls, session: AsyncSession, user_id: UUID) -> List[Session]:
        """
        Возвращает все игровые сессии (Session), в которых участвует пользователь (User).
        Использует связь через SessionUser.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            user_id (UUID): Идентификатор пользователя.
        
        Returns:
            List[Session]: Список сессий пользователя.
        """
        # JOIN с SessionUser
        result = await session.execute(
            select(cls.model)
            .join(SessionUser, cls.model.id == SessionUser.session_id)
            .where(SessionUser.user_id == user_id)
        )
        return result.scalars().all()

class SessionUserDAO(BaseDAO):
    model = SessionUser

    @classmethod
    async def add_user_to_session(cls, session: AsyncSession, data: dict) -> SessionUser:
        """
        Добавляет пользователя (User) в игровую сессию (Session) через промежуточную таблицу SessionUser.
        Проверяет, что пользователь еще не состоит в этой сессии.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для добавления. Ожидаемые ключи:
                - session_id (UUID): ID сессии
                - user_id (UUID): ID пользователя
                - permission (str): Права пользователя в сессии
        
        Returns:
            SessionUser: Созданный объект связи.
        
        Raises:
            ValueError: Если пользователь уже состоит в сессии.
        """
        if await cls.exists_by(session, session_id=data["session_id"], user_id=data["user_id"]):
            log.error(layer='DAO', component='SessionUserDAO.add_user_to_session', message=f'User {data["user_id"]} already in session {data["session_id"]}')
            raise ValueError("User is already in this session")
        
        log.info(layer='DAO', component='SessionUserDAO.add_user_to_session', message=f'Adding user {data["user_id"]} to session {data["session_id"]}')
        return await cls.create_one(session, data)

    @classmethod
    async def get_session_users_with_user_data(cls, session: AsyncSession, session_id: UUID) -> List[dict]:
        """
        Возвращает список пользователей (User) и их связей (SessionUser) для заданной игровой сессии.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            session_id (UUID): Идентификатор сессии.
        
        Returns:
            List[dict]: Список словарей с ключами 'session_user' (SessionUser) и 'user' (User).
        """
        # JOIN с User
        result = await session.execute(
            select(SessionUser, User)
            .join(User, SessionUser.user_id == User.id)
            .where(SessionUser.session_id == session_id)
        )
        return [{"session_user": su, "user": u} for su, u in result.all()]

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def create_user_unique(cls, session: AsyncSession, data: dict) -> User:
        """
        Создает нового пользователя (User) с проверкой уникальности login.
        
        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            data (dict): Данные для создания пользователя. Ожидаемые ключи:
                - login (str): Логин пользователя (уникальный)
                - password (str): Хешированный пароль
                - mail (str, optional): Email пользователя
        
        Returns:
            User: Созданный объект пользователя.
        
        Raises:
            IntegrityError: Если login уже существует.
        """
        if await cls.exists_by(session, login=data["login"]):
            log.error(layer='DAO', component='UserDAO.create_user_unique', message=f'User with login {data["login"]} already exists')
            raise IntegrityError("User with this login already exists", None, None)
        
        log.info(layer='DAO', component='UserDAO.create_user_unique', message=f'Creating User with login {data["login"]}')
        return await cls.create_one(session, data)

class PlayerEffectsDAO(BaseDAO):
    model = PlayerEffects

