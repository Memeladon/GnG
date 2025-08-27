import random
from typing import Optional, List, Dict, Any
from uuid import UUID

from src.database.postgres.dao.dao import PlayerDAO, PlayerStatsDAO, InventoryDAO, UserDAO
from src.services.base_service import BaseService
from src.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerWithRelations, PlayerWithFullData
from src.schemas.player_stats import PlayerStatsCreate, PlayerStatsResponse
from src.schemas.inventory import InventoryCreate, InventoryResponse
from src.database.postgres.sql_enums import UserRights
from src.database.postgres.dao.base import connection
from src.utils.logger import log


class PlayerService(BaseService):
    """Сервис для работы с игроками"""
    
    def __init__(self):
        super().__init__(PlayerDAO)
    
    @connection
    async def create_player_profile(self, player_data: PlayerCreate, session) -> PlayerWithRelations:
        """
        Создание профиля игрока с инвентарем и статистикой
        
        Args:
            player_data: данные игрока
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            PlayerWithRelations: созданный игрок со связанными данными
            
        Raises:
            ValueError: если пользователь уже имеет профиль игрока
        """
        # Проверяем, не имеет ли пользователь уже профиль игрока
        if await self.exists_by({'user_id': player_data.user_id}, session):
            raise ValueError("Пользователь уже имеет профиль игрока")
        
        # Проверяем уникальность username
        if await self.exists_by({'username': player_data.username}, session):
            raise ValueError(f"Игрок с именем '{player_data.username}' уже существует")
        
        # Создаем инвентарь
        inventory = await InventoryDAO.create_one(session, {
            'player_id': player_data.user_id
        })
        
        # Создаем игрока
        player_dict = player_data.model_dump()
        player_dict['inventory_id'] = inventory.id
        
        player = await self.dao.create_player_first_time(session, player_dict)
        
        return PlayerWithRelations.model_validate(player)
    
    @connection
    async def roll_dice(self, player_id: UUID, modifiers: Dict[str, int] = None, session=None) -> Dict[str, Any]:
        """
        Бросок кубика для игрока
        
        Args:
            player_id: ID игрока
            modifiers: модификаторы (dice_modifier, game_modifier)
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            Dict с результатом броска
        """
        player = await self.get_by_id(player_id, session)
        if not player:
            raise ValueError("Игрок не найден")
        
        # Базовый бросок кубика (1-6)
        dice_value = random.randint(1, 6)
        
        # Применяем модификаторы
        dice_modifier = modifiers.get('dice_modifier', 0) if modifiers else 0
        game_modifier = modifiers.get('game_modifier', 0) if modifiers else 0
        
        final_value = max(1, min(6, dice_value + dice_modifier))
        
        # Обновляем последнее значение кубика
        await self.update({
            'id': player_id,
            'last_dice_value': final_value
        }, session)
        
        return {
            'dice_value': dice_value,
            'dice_modifier': dice_modifier,
            'game_modifier': game_modifier,
            'final_value': final_value
        }
    
    @connection
    async def move_player(self, player_id: UUID, steps: int, session=None) -> PlayerResponse:
        """
        Перемещение игрока по полю
        
        Args:
            player_id: ID игрока
            steps: количество шагов
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            PlayerResponse: обновленный игрок
        """
        player = await self.get_by_id(player_id, session)
        if not player:
            raise ValueError("Игрок не найден")
        
        # Простое перемещение (можно расширить логикой поля)
        new_cell_id = (player.cell_id + steps) % 30  # Предполагаем 30 клеток
        
        updated_player = await self.update({
            'id': player_id,
            'cell_id': new_cell_id
        }, session)
        
        return PlayerResponse.model_validate(updated_player)
    
    @connection
    async def update_player_stats(self, player_id: UUID, stats_data: Dict[str, Any], session=None) -> PlayerStatsResponse:
        """
        Обновление статистики игрока
        
        Args:
            player_id: ID игрока
            stats_data: данные для обновления статистики
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            PlayerStatsResponse: обновленная статистика
        """
        player = await self.get_one(player_id, session)
        if not player:
            raise ValueError("Игрок не найден")
        
        stats = await PlayerStatsDAO.get_one(session, player_id)
        if not stats:
            raise ValueError("Статистика игрока не найдена")
        
        # Добавляем ID статистики для обновления
        stats_data['id'] = stats.id
        
        updated_stats = await PlayerStatsDAO.update_one(session, stats_data)
        return PlayerStatsResponse.model_validate(updated_stats)
    
    @connection
    async def get_player_with_full_data(self, player_id: UUID, session=None) -> Optional[PlayerWithFullData]:
        """Получение игрока со всеми данными включая предметы"""
        player = await self.dao.get_one(session, player_id)
        if not player:
            return None
        return PlayerWithFullData.model_validate(player)
    
    @connection
    async def get_players_by_session(self, session_id: UUID, session=None) -> List[PlayerWithRelations]:
        """Получение всех игроков в сессии"""
        players = await self.dao.get_players_by_session_id(session, session_id)
        return [PlayerWithRelations.model_validate(player) for player in players]
    
    @connection
    async def update_player_profile(self, player_id: UUID, update_data: PlayerUpdate, session=None) -> Optional[PlayerResponse]:
        """Обновление профиля игрока"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict['player_id'] = player_id
        
        player = await self.dao.update_player_profile(session, update_dict)
        if not player:
            return None
        
        return PlayerResponse.model_validate(player)
    
    @connection
    async def get_player_stats(self, player_id: UUID, session=None) -> Optional[PlayerStatsResponse]:
        """Получение статистики игрока"""
        stats = await PlayerStatsDAO.get_one(session, player_id)
        if not stats:
            return None
        return PlayerStatsResponse.model_validate(stats)
    
    @connection
    async def get_player_inventory(self, player_id: UUID, session=None) -> Optional[InventoryResponse]:
        """Получение инвентаря игрока"""
        player = await self.get_by_id(player_id, session)
        if not player:
            return None
        
        inventory = await InventoryDAO.get_one(session, player.inventory_id)
        if not inventory:
            return None
        
        return InventoryResponse.model_validate(inventory)
    
    @connection
    async def add_game_completion(self, player_id: UUID, hours_played: float, game_completed: bool = True, session=None) -> PlayerStatsResponse:
        """
        Добавление завершенной игры в статистику игрока
        
        Args:
            player_id: ID игрока
            hours_played: количество часов прохождения
            game_completed: завершена ли игра успешно
            session: сессия базы данных (автоматически передается декоратором)
            
        Returns:
            PlayerStatsResponse: обновленная статистика
        """
        player = await self.get_by_id(player_id, session)
        if not player:
            raise ValueError("Игрок не найден")
        
        stats = await PlayerStatsDAO.get_one(session, player_id)
        if not stats:
            raise ValueError("Статистика игрока не найдена")
        
        # Обновляем статистику
        update_data = {
            'id': stats.id,
            'games_completed': stats.games_completed + (1 if game_completed else 0),
            'total_points': stats.total_points + (hours_played * 10 if game_completed else 0),  # Примерная формула
            'games_dropped': stats.games_dropped + (0 if game_completed else 1)
        }
        
        updated_stats = await PlayerStatsDAO.update_one(session, update_data)
        return PlayerStatsResponse.model_validate(updated_stats)
    
