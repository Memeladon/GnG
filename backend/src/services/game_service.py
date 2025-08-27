import random
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from src.database.postgres.dao.dao import GameDAO, PlayerStatsDAO
from src.services.base_service import BaseService
from src.schemas.game import GameCreate, GameUpdate, GameResponse, GameShortInfo
from src.database.postgres.sql_enums import GameStatus
from src.database.postgres.dao.base import connection
from src.services.player_service import PlayerService
from src.utils.logger import log
from src.schemas import ServiceResult


class GameService(BaseService):
    """
    Сервис для работы с записями о прохождении игр игроками
    """
    def __init__(self):
        super().__init__(GameDAO)
        self.player_service = PlayerService()

    async def _update_player_stats_for_game_status(self, session, player_id: UUID, old_status: GameStatus, new_status: GameStatus):
        """Приватный метод для обновления статистики игрока при смене статуса игры."""
        stats = await PlayerStatsDAO.find_one_by(session, player_id=player_id)
        if not stats:
            raise ValueError(f"Player stats not found for player_id={player_id}")
        stats_update = {'id': stats.id}
        if new_status == GameStatus.PROGRESS:
            if old_status == GameStatus.COMPLETED:
                stats_update['count_completed_games'] = max((stats.count_completed_games or 0) - 1, 0)
            elif old_status == GameStatus.DROPPED:
                stats_update['count_dropped_games'] = max((stats.count_dropped_games or 0) - 1, 0)
            elif old_status == GameStatus.REROLLED:
                stats_update['count_rerolled_games'] = max((stats.count_rerolled_games or 0) - 1, 0)
        elif new_status == GameStatus.COMPLETED and old_status != GameStatus.COMPLETED:
            stats_update['count_completed_games'] = (stats.count_completed_games or 0) + 1
        elif new_status == GameStatus.DROPPED and old_status != GameStatus.DROPPED:
            stats_update['count_dropped_games'] = (stats.count_dropped_games or 0) + 1
        elif new_status == GameStatus.REROLLED and old_status != GameStatus.REROLLED:
            stats_update['count_rerolled_games'] = (stats.count_rerolled_games or 0) + 1
        if len(stats_update) > 1:
            await PlayerStatsDAO.update_one(session, stats_update)

    @connection
    async def create_game(self, data: Dict[str, Any], session) -> ServiceResult[GameResponse]:
        """
        Создать запись о попытке прохождения игры игроком (Game).
        Обновляет статистику игрока (total_games), если статус не PROGRESS.
        Транзакция: создание игры + обновление статистики.
        Args:
            data (dict): см. GameCreate
        Returns:
            ServiceResult[GameResponse]
        """
        try:
            game_create = GameCreate(**data)
        except Exception as e:
            log.error(message=f"create_game: invalid data {data} -> {e}")
            return ServiceResult(success=False, message=f"Invalid game data: {e}")
        async with session.begin():
            game_dict = game_create.model_dump()
            game_dict['created_at'] = datetime.now().isoformat()
            game = await self.create(game_dict, session)
            if game.status != GameStatus.PROGRESS:
                await self._update_player_stats_for_game_status(session, game.player_id, GameStatus.PROGRESS, game.status)
        log.info(message=f"create_game: {game_dict} -> OK id={game.id}")
        return ServiceResult(success=True, data=GameResponse.model_validate(game))

    @connection
    async def update_game_status(self, game_id: int, params: Dict[str, Any], session=None) -> ServiceResult[GameResponse]:
        """
        Обновить статус, часы, отзыв, очки для записи Game. Корректно обновляет статистику игрока при изменении статуса.
        Args:
            game_id (int)
            params (dict): см. schemas/game/GameUpdate
        Returns:
            ServiceResult[GameResponse]
        """
        game = await self.get_by_id(game_id, session)
        if not game:
            log.warning(message=f"update_game_status: game_id={game_id} not found")
            return ServiceResult(success=False, message=f"Game with id={game_id} not found")
        try:
            update_data = GameUpdate(**params).model_dump(exclude_unset=True)
        except Exception as e:
            log.error(message=f"update_game_status: invalid params {params} -> {e}")
            return ServiceResult(success=False, message=f"Invalid update data: {e}")
        old_status = game.status
        new_status = update_data.get('status', old_status)
        update_data['id'] = game_id
        async with session.begin():
            updated_game = await self.update(update_data, session)
            if new_status != old_status:
                await self._update_player_stats_for_game_status(session, game.player_id, old_status, new_status)
        log.info(message=f"update_game_status: id={game_id} {params} -> OK")
        return ServiceResult(success=True, data=GameResponse.model_validate(updated_game))

    @connection
    async def get_game_short_info(self, player_id: UUID, page: int = 1, page_size: int = 20, order_by: str = None, desc_order: bool = None, session=None) -> ServiceResult[List[GameShortInfo]]:
        """
        Получить краткую информацию по всем играм игрока с пагинацией и сортировкой.
        Args:
            player_id (UUID)
            page (int): номер страницы
            page_size (int): размер страницы
            order_by (str, optional): поле сортировки
            desc_order (bool, optional): по убыванию
        Returns:
            ServiceResult[List[GameShortInfo]]
        """
        offset = (page - 1) * page_size
        all_games = await self.find_by({'player_id': player_id}, session)
        if order_by:
            all_games = sorted(all_games, key=lambda g: getattr(g, order_by, None), reverse=bool(desc_order))
        paginated = all_games[offset:offset+page_size]
        log.debug(message=f"get_game_short_info: player_id={player_id} page={page} size={page_size} -> {len(paginated)} items")
        return ServiceResult(success=True, data=[GameShortInfo.model_validate(game) for game in paginated])

    @connection
    async def get_games_by_player(self, player_id: UUID, status: Optional[GameStatus] = None, page: int = 1, page_size: int = 20, order_by: str = None, desc_order: bool = None, session=None) -> ServiceResult[List[GameResponse]]:
        """
        Получить все записи Game игрока, опционально с фильтрацией по статусу, пагинацией и сортировкой.
        Args:
            player_id (UUID)
            status (GameStatus, optional)
            page (int)
            page_size (int)
            order_by (str, optional)
            desc_order (bool, optional)
        Returns:
            ServiceResult[List[GameResponse]]
        """
        filters = {'player_id': player_id}
        if status:
            filters['status'] = status
        offset = (page - 1) * page_size
        all_games = await self.find_by(filters, session)
        if order_by:
            all_games = sorted(all_games, key=lambda g: getattr(g, order_by, None), reverse=bool(desc_order))
        paginated = all_games[offset:offset+page_size]
        log.debug(message=f"get_games_by_player: player_id={player_id} status={status} page={page} size={page_size} -> {len(paginated)} items")
        return ServiceResult(success=True, data=[GameResponse.model_validate(game) for game in paginated])

    @connection
    async def get_last_game_short_info(self, player_id: UUID, session=None) -> ServiceResult[GameShortInfo]:
        """
        Получить краткую информацию по самой последней (по дате создания) записи Game игрока.
        Args:
            player_id (UUID)
        Returns:
            ServiceResult[GameShortInfo]
        """
        games = await self.find_by({'player_id': player_id}, session)
        if not games:
            return ServiceResult(success=False, message=f"No games found for player_id={player_id}")
        last_game = max(games, key=lambda g: getattr(g, 'created_at', None) or datetime.min)
        return ServiceResult(success=True, data=GameShortInfo.model_validate(last_game))

    @connection
    async def get_game_full(self, game_id: int, session=None) -> ServiceResult[GameResponse]:
        """
        Получить полную информацию по одной записи Game.
        Args:
            game_id (int)
        Returns:
            ServiceResult[GameResponse]
        """
        game = await self.get_by_id(game_id, session)
        if not game:
            log.warning(message=f"get_game_full: game_id={game_id} not found")
            return ServiceResult(success=False, message=f"Game with id={game_id} not found")
        log.debug(message=f"get_game_full: id={game_id} -> OK")
        return ServiceResult(success=True, data=GameResponse.model_validate(game))

    @connection
    async def get_active_games(self, session=None) -> ServiceResult[List[GameResponse]]:
        """Получение всех активных игр"""
        games = await self.find_by({'status': GameStatus.PROGRESS}, session)
        return ServiceResult(success=True, data=[GameResponse.model_validate(game) for game in games])
    
    @connection
    async def get_completed_games(self, session=None) -> ServiceResult[List[GameResponse]]:
        """Получение всех пройденных игр"""
        games = await self.find_by({'status': GameStatus.COMPLETED}, session)
        return ServiceResult(success=True, data=[GameResponse.model_validate(game) for game in games])
    
    @connection
    async def get_dropped_games(self, session=None) -> ServiceResult[List[GameResponse]]:
        """Получение всех дропнутых игр"""
        games = await self.find_by({'status': GameStatus.DROP}, session)
        return ServiceResult(success=True, data=[GameResponse.model_validate(game) for game in games])
    
    @connection
    async def get_rerolled_games(self, session=None) -> ServiceResult[List[GameResponse]]:
        """Получение всех рерольнутых игр"""
        games = await self.find_by({'status': GameStatus.REROLLED}, session)
        return ServiceResult(success=True, data=[GameResponse.model_validate(game) for game in games])

    @connection
    async def delete_game(self, game_id: int, session=None) -> ServiceResult[None]:
        """
        Удалить запись Game по id.
        Args:
            game_id (int): ID записи Game
        Raises:
            ValueError: если запись не найдена
        Пример:
            await service.delete_game(123)
        Returns:
            ServiceResult[None]
        """
        game = await self.get_by_id(game_id, session)
        if not game:
            log.warning(message=f"delete_game: game_id={game_id} not found")
            return ServiceResult(success=False, message=f"Game with id={game_id} not found")
        await self.delete(game_id, session)
        log.info(message=f"delete_game: id={game_id} -> DELETED")
        return ServiceResult(success=True, data=None)