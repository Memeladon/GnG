import random
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from src.database.postgres.dao.dao import CellDAO, GameDAO, PlayerDAO, SessionDAO
from src.services.base_service import BaseService
from src.schemas.cell import CellPydantic
from src.schemas.game import GamePydantic, GameCreate, GameUpdate, GameResponse, GameWithPlayers
from src.schemas.player import PlayerResponse
from src.database.postgres.sql_enums import GameStatus
from src.database.postgres.dao.base import connection
from src.utils.logger import log
from src.schemas import ServiceResult


class CellService(BaseService):
    """
    Сервис для работы с клетками поля
    """
    def __init__(self):
        super().__init__(CellDAO)
    
    @connection
    async def get_cell_info(self, cell_id: int, session=None) -> Optional[CellPydantic]:
        """Получение информации о клетке"""
        cell = await self.get_one(session, cell_id)
        if not cell:
            return None
        return CellPydantic.model_validate(cell)
    
    @connection
    async def get_all_cells(self, session=None) -> List[CellPydantic]:
        """Получение всех клеток игрового поля"""
        cells = await self.get_all(session)
        return [CellPydantic.model_validate(cell) for cell in cells]

    @connection
    async def add_effect_to_cell(self, cell_id: int, effect: str, acting_user_id: str, session=None):
        """
        Добавить эффект/ловушку на клетку.
        Игрок может только на свою клетку, админ/модератор — на любую.
        """
        cell = await self.get_one(session, cell_id)
        if not cell:
            log.warning(message=f"add_effect_to_cell: cell_id={cell_id} not found")
            raise ValueError("Cell not found")
        
        acting_player = await PlayerDAO.find_one_by(session, user_id=acting_user_id)
        if not acting_player:
            raise ValueError("Acting user is not a player")
        
        # Игрок может только на свою клетку
        if acting_player.role not in ['ADMIN', 'MODERATOR'] and acting_player.cell_id != cell_id:
            log.warning(message=f"add_effect_to_cell: user {acting_user_id} tried to add effect to not own cell")
            raise PermissionError("You can add effect only to your current cell")
        
        if effect in cell.effects:
            log.warning(message=f"add_effect_to_cell: effect '{effect}' already on cell {cell_id}")
            raise ValueError("Effect already present on cell")
        cell.effects.append(effect)
        await self.update(session, {'id': cell_id, 'effects': cell.effects})
        log.info(message=f"add_effect_to_cell: effect '{effect}' added to cell {cell_id} by {acting_user_id}")
        return ServiceResult(success=True, data=CellPydantic.model_validate(cell))

    @connection
    async def remove_effect_from_cell(self, cell_id: int, effect: str, acting_user_id: str, session=None):
        """
        Удалить эффект/ловушку с клетки (только админ/модератор).
        """
        cell = await self.get_one(session, cell_id)
        if not cell:
            log.warning(message=f"remove_effect_from_cell: cell_id={cell_id} not found")
            raise ValueError("Cell not found")
        acting_player = await PlayerDAO.find_one_by(session, user_id=acting_user_id)
        if not acting_player or acting_player.role not in ['ADMIN', 'MODERATOR']:
            log.warning(message=f"remove_effect_from_cell: user {acting_user_id} has no rights")
            raise PermissionError("Only admin or moderator can remove effects")
        if effect not in cell.effects:
            log.warning(message=f"remove_effect_from_cell: effect '{effect}' not found on cell {cell_id}")
            raise ValueError("Effect not present on cell")
        cell.effects.remove(effect)
        await self.update(session, {'id': cell_id, 'effects': cell.effects})
        log.info(message=f"remove_effect_from_cell: effect '{effect}' removed from cell {cell_id} by {acting_user_id}")
        return ServiceResult(success=True, data=CellPydantic.model_validate(cell))

    @connection
    async def move_player(self, player_id: str, target_cell_id: int, acting_user_id: str, session=None):
        """
        Переместить фишку игрока на другую клетку.
        Игрок может только свою, админ/модератор — любую.
        """
        player = await PlayerDAO.get_one(session, player_id)
        if not player:
            log.warning(message=f"move_player: player_id={player_id} not found")
            raise ValueError("Player not found")
        acting_player = await PlayerDAO.find_one_by(session, user_id=acting_user_id)
        if not acting_player:
            raise ValueError("Acting user is not a player")
        if acting_player.role not in ['ADMIN', 'MODERATOR'] and acting_player.id != player_id:
            log.warning(message=f"move_player: user {acting_user_id} tried to move not own token")
            raise PermissionError("You can move only your own token")
        await PlayerDAO.update_one(session, {'id': player_id, 'cell_id': target_cell_id})
        log.info(message=f"move_player: player_id={player_id} moved to cell {target_cell_id} by {acting_user_id}")
        return ServiceResult(success=True, data=CellPydantic.model_validate(player))

    @connection
    async def apply_item_effect_to_cell(self, item_instance, cell_id: int, acting_user_id: str, session=None):
        """
        Применить эффект предмета к клетке (например, оставить след жижи).
        """
        # Пример для "Липкая жижа" (item_id == 52, заменить на свой id)
        if getattr(item_instance, 'item_id', None) == 52:
            cell = await self.get_one(session, cell_id)
            effects = cell.effects or {}
            if "slime_trace" in effects:
                log.warning(message=f"apply_item_effect_to_cell: slime_trace already on cell {cell_id}")
                raise ValueError("Slime trace already present on cell")
            effects["slime_trace"] = acting_user_id
            await self.update(session, {'id': cell_id, 'effects': effects})
            log.info(message=f"apply_item_effect_to_cell: slime_trace by {acting_user_id} on cell {cell_id}")
            return ServiceResult(success=True, data=CellPydantic.model_validate(cell))
        # ... другие предметы/эффекты
        return ServiceResult(success=False, message="Item effect application logic not implemented")

 