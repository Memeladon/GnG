from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database.postgres.dao.dao import PlayerEffectsDAO, CellDAO, ItemInstanceDAO
from src.database.postgres.models import PlayerEffects, Cell
from src.database.postgres.sql_enums import EffectType, EffectCategory
from src.services.base_service import BaseService
from src.utils.logger import log
from src.database.postgres.dao.base import connection
from src.schemas import ServiceResult
from src.schemas.player_effects import PlayerEffectsResponse


class EffectsService(BaseService):
    """
    Сервис для работы с эффектами игроков и ловушками на клетках
    """
    def __init__(self):
        super().__init__(PlayerEffectsDAO)

    # ==================== ЭФФЕКТЫ ИГРОКА ====================

    @connection
    async def add_player_effect(self, player_id: UUID, effect_name: str, effect_type: EffectType, 
                               effect_category: EffectCategory, turns_remaining: int = 0, 
                               effect_data: dict = None, item_instance_id: int = None, session=None) -> ServiceResult:
        """
        Добавляет эффект игроку.
        
        Args:
            player_id (UUID): ID игрока
            effect_name (str): Название эффекта
            effect_type (EffectType): Тип эффекта
            effect_category (EffectCategory): Категория эффекта
            turns_remaining (int): Сколько ходов осталось (0 для бесконечных)
            effect_data (dict): Дополнительные данные эффекта
            item_instance_id (int, optional): ID экземпляра предмета, связанного с эффектом
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Результат операции
        """
        effect_data = effect_data or {}
        
        effect = await PlayerEffectsDAO.create_one(session, {
            "player_id": player_id,
            "effect_name": effect_name,
            "effect_type": effect_type,
            "effect_category": effect_category,
            "turns_remaining": turns_remaining,
            "effect_data": effect_data,
            "item_instance_id": item_instance_id
        })
        
        log.info(layer='SERVICE', component='EffectsService.add_player_effect', 
                message=f'Добавлен эффект {effect_name} игроку {player_id}')
        
        return ServiceResult(success=True, data=PlayerEffectsResponse.model_validate(effect))

    @connection
    async def get_player_effects(self, player_id: UUID, effect_type: Optional[EffectType] = None, 
                                session=None) -> List[PlayerEffects]:
        """
        Получает эффекты игрока.
        
        Args:
            player_id (UUID): ID игрока
            effect_type (EffectType, optional): Фильтр по типу эффекта
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            List[PlayerEffects]: Список эффектов
        """
        filters = {"player_id": player_id, "is_active": True}
        if effect_type:
            filters["effect_type"] = effect_type
            
        effects = await PlayerEffectsDAO.get_many(session, filters)
        
        log.info(layer='SERVICE', component='EffectsService.get_player_effects', 
                message=f'Получено {len(effects)} эффектов для игрока {player_id}')
        
        return effects

    @connection
    async def decrement_effect_turns(self, player_id: UUID, session=None) -> ServiceResult:
        """
        Уменьшает количество ходов для всех активных эффектов игрока.
        Удаляет эффекты с истекшим временем.
        
        Args:
            player_id (UUID): ID игрока
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Информация об удаленных эффектах
        """
        effects = await self.get_player_effects(player_id, session=session)
        expired_effects = []
        
        for effect in effects:
            if effect.turns_remaining is not None and effect.turns_remaining > 0:  # Пропускаем бесконечные эффекты
                effect.turns_remaining -= 1
                
                if effect.turns_remaining <= 0:
                    expired_effects.append(effect.effect_name)
                    await PlayerEffectsDAO.delete_one(session, effect.id)
                else:
                    await PlayerEffectsDAO.update_one(session, {
                        "id": effect.id,
                        "turns_remaining": effect.turns_remaining
                    })
        
        if expired_effects:
            log.info(layer='SERVICE', component='EffectsService.decrement_effect_turns', 
                    message=f'Истекли эффекты игрока {player_id}: {expired_effects}')
        
        return ServiceResult(success=True, data={
            "expired_effects": expired_effects,
            "remaining_effects": len(effects) - len(expired_effects)
        })

    @connection
    async def remove_player_effect(self, player_id: UUID, effect_name: str, session=None) -> ServiceResult:
        """
        Удаляет конкретный эффект игрока.
        
        Args:
            player_id (UUID): ID игрока
            effect_name (str): Название эффекта
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: True если эффект удален
        """
        effects = await PlayerEffectsDAO.get_many(session, {
            "player_id": player_id,
            "effect_name": effect_name,
            "is_active": True
        })
        
        if effects:
            await PlayerEffectsDAO.delete_one(session, effects[0].id)
            log.info(layer='SERVICE', component='EffectsService.remove_player_effect', 
                    message=f'Удален эффект {effect_name} у игрока {player_id}')
            return ServiceResult(success=True)
        
        return ServiceResult(success=False)

    # ==================== ЛОВУШКИ НА КЛЕТКАХ ====================

    @connection
    async def add_cell_trap(self, cell_id: int, created_by_player_id: UUID, trap_name: str,
                           uses_remaining: int = 1, trap_data: dict = None, session=None) -> ServiceResult:
        """
        Добавляет ловушку на клетку.
        
        Args:
            cell_id (int): ID клетки
            created_by_player_id (UUID): ID игрока, создавшего ловушку
            trap_name (str): Название ловушки
            uses_remaining (int): Сколько раз можно использовать
            trap_data (dict): Дополнительные данные ловушки
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Результат операции
        """
        cell = await CellDAO.get_one(session, cell_id)
        if not cell:
            return ServiceResult(success=False, message="Клетка не найдена")
        
        trap_data = trap_data or {}
        
        # Добавляем ловушку в JSON поле
        cell.traps[trap_name] = {
            "created_by": str(created_by_player_id),
            "uses_remaining": uses_remaining,
            "data": trap_data
        }
        
        await CellDAO.update_one(session, {
            "id": cell_id,
            "traps": cell.traps
        })
        
        log.info(layer='SERVICE', component='EffectsService.add_cell_trap', 
                message=f'Добавлена ловушка {trap_name} на клетку {cell_id}')
        
        return ServiceResult(success=True, data={"trap_name": trap_name})

    @connection
    async def get_cell_traps(self, cell_id: int, session=None) -> Dict[str, Any]:
        """
        Получает ловушки на клетке.
        
        Args:
            cell_id (int): ID клетки
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            Dict[str, Any]: Словарь ловушек на клетке
        """
        cell = await CellDAO.get_one(session, cell_id)
        if not cell:
            return {}
        
        return cell.traps

    @connection
    async def use_cell_trap(self, cell_id: int, trap_name: str, session=None) -> ServiceResult:
        """
        Использует ловушку на клетке.
        
        Args:
            cell_id (int): ID клетки
            trap_name (str): Название ловушки
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Информация о ловушке
        """
        cell = await CellDAO.get_one(session, cell_id)
        if not cell or trap_name not in cell.traps:
            return ServiceResult(success=False, message="Ловушка не найдена")
        
        trap = cell.traps[trap_name]
        
        # Уменьшаем количество использований
        if trap["uses_remaining"] > 0:
            trap["uses_remaining"] -= 1
            
            if trap["uses_remaining"] <= 0:
                # Удаляем ловушку
                del cell.traps[trap_name]
                log.info(layer='SERVICE', component='EffectsService.use_cell_trap', 
                        message=f'Ловушка {trap_name} использована и удалена с клетки {cell_id}')
            else:
                log.info(layer='SERVICE', component='EffectsService.use_cell_trap', 
                        message=f'Ловушка {trap_name} использована, осталось {trap["uses_remaining"]}')
            
            # Обновляем клетку
            await CellDAO.update_one(session, {
                "id": cell_id,
                "traps": cell.traps
            })
        
        return ServiceResult(success=True, data={
            "trap_name": trap_name,
            "trap_data": trap.get("data", {}),
            "uses_remaining": trap["uses_remaining"]
        })

    @connection
    async def remove_cell_trap(self, cell_id: int, trap_name: str, session=None) -> ServiceResult:
        """
        Удаляет ловушку с клетки.
        
        Args:
            cell_id (int): ID клетки
            trap_name (str): Название ловушки
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: True если ловушка удалена
        """
        cell = await CellDAO.get_one(session, cell_id)
        if not cell or trap_name not in cell.traps:
            return ServiceResult(success=False)
        
        del cell.traps[trap_name]
        
        await CellDAO.update_one(session, {
            "id": cell_id,
            "traps": cell.traps
        })
        
        log.info(layer='SERVICE', component='EffectsService.remove_cell_trap', 
                message=f'Удалена ловушка {trap_name} с клетки {cell_id}')
        
        return ServiceResult(success=True)

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    @connection
    async def check_effect_conflicts(self, player_id: UUID, session=None) -> ServiceResult:
        """
        Проверяет конфликты между эффектами игрока.
        
        Args:
            player_id (UUID): ID игрока
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Информация о конфликтах
        """
        effects = await self.get_player_effects(player_id, session=session)
        conflicts = []
        
        # Проверяем конфликты между эффектами
        effect_names = [effect.effect_name for effect in effects]
        
        # Читерский кубик + Кубик хуюбика
        if "Читерский кубик" in effect_names and "Кубик хуюбика" in effect_names:
            conflicts.append({
                "type": "destruction",
                "effects": ["Читерский кубик", "Кубик хуюбика"],
                "description": "Предметы уничтожают друг друга"
            })
        
        # Очки EZ + Повязка Рэмбо
        if "Очки EZ" in effect_names and "Повязка Рэмбо" in effect_names:
            conflicts.append({
                "type": "destruction",
                "effects": ["Очки EZ", "Повязка Рэмбо"],
                "description": "Предметы уничтожают друг друга"
            })
        
        return ServiceResult(success=True, data={
            "conflicts": conflicts,
            "total_effects": len(effects)
        })

    @connection
    async def resolve_effect_conflicts(self, player_id: UUID, session=None) -> ServiceResult:
        """
        Разрешает конфликты между эффектами игрока.
        
        Args:
            player_id (UUID): ID игрока
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Результат разрешения конфликтов
        """
        conflicts = await self.check_effect_conflicts(player_id, session=session)
        resolved_conflicts = []
        
        for conflict in conflicts["conflicts"]:
            if conflict["type"] == "destruction":
                for effect_name in conflict["effects"]:
                    if await self.remove_player_effect(player_id, effect_name, session=session):
                        resolved_conflicts.append(effect_name)
        
        return ServiceResult(success=True, data={
            "resolved_conflicts": resolved_conflicts
        })

    @connection
    async def on_game_completed(self, player_id: UUID, session=None) -> ServiceResult:
        """
        Вызывается при завершении игры игроком.
        Уменьшает количество ходов для всех активных эффектов.
        Удаляет эффекты от использованных предметов (с несуществующими item_instance_id).
        
        Args:
            player_id (UUID): ID игрока
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Информация об обновленных эффектах
        """
        # Сначала удаляем эффекты от использованных предметов
        effects = await PlayerEffectsDAO.get_many(session, {
            "player_id": player_id,
            "is_active": True
        })
        
        removed_effects = []
        for effect in effects:
            if effect.item_instance_id:
                # Проверяем, существует ли еще ItemInstance
                item_instance = await ItemInstanceDAO.get_one(session, effect.item_instance_id)
                if not item_instance:
                    # ItemInstance не существует (был использован), удаляем эффект
                    await PlayerEffectsDAO.delete_one(session, effect.id)
                    removed_effects.append(effect.effect_name)
        
        # Затем уменьшаем ходы для оставшихся эффектов
        result = await self.decrement_effect_turns(player_id, session=session)
        
        if removed_effects:
            log.info(layer='SERVICE', component='EffectsService.on_game_completed', 
                    message=f'Удалены эффекты от использованных предметов игрока {player_id}: {removed_effects}')
            result["removed_item_effects"] = removed_effects
        
        return result

    @connection
    async def remove_effects_by_item_instance(self, item_instance_id: int, session=None) -> ServiceResult:
        """
        Удаляет все эффекты, связанные с конкретным экземпляром предмета.
        
        Args:
            item_instance_id (int): ID экземпляра предмета
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            ServiceResult: Информация об удаленных эффектах
        """
        effects = await PlayerEffectsDAO.get_many(session, {
            "item_instance_id": item_instance_id,
            "is_active": True
        })
        
        removed_effects = []
        for effect in effects:
            await PlayerEffectsDAO.delete_one(session, effect.id)
            removed_effects.append(effect.effect_name)
        
        if removed_effects:
            log.info(layer='SERVICE', component='EffectsService.remove_effects_by_item_instance', 
                    message=f'Удалены эффекты от ItemInstance {item_instance_id}: {removed_effects}')
        
        return ServiceResult(success=True, data={
            "removed_effects": removed_effects,
            "count": len(removed_effects)
        }) 