from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.dao.dao import PlayerDAO
from src.services.base_service import BaseService
from src.services.player_service import PlayerService
from src.services.effects_service import EffectsService
from src.utils.logger import log
from src.database.postgres.dao.base import connection
from src.database.postgres.models import Player


class DiceService(BaseService):
    """
    Сервис для работы с кубиками и их модификаторами
    """
    def __init__(self):
        super().__init__(PlayerDAO)
        self.player_service = PlayerService()
        self.effects_service = EffectsService()

    @connection
    async def roll_dice(self, player_id: UUID, dice1: int, dice2: int, 
                       cheat_dice_index: Optional[int] = None, 
                       cheat_dice_value: Optional[int] = None,
                       session=None) -> Dict[str, Any]:
        """
        Бросает кубики с учетом модификаторов игрока.
        
        Args:
            player_id (UUID): Идентификатор игрока.
            dice1 (int): Значение первого кубика (1-6).
            dice2 (int): Значение второго кубика (1-6).
            cheat_dice_index (int, optional): Индекс кубика для замены (0 или 1).
            cheat_dice_value (int, optional): Новое значение для кубика.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            dict: {
                "original_dice": [dice1, dice2],
                "modified_dice": [modified_dice1, modified_dice2],
                "total_value": int,  # Сумма для движения
                "modifiers_applied": list,  # Какие модификаторы сработали
                "new_position": int,  # Новая позиция игрока
                "passed_start": bool  # Прошел ли через старт
            }
        
        Raises:
            ValueError: Если игрок не найден или значения кубиков некорректны.
        """
        log.info(layer='SERVICE', component='DiceService.roll_dice', message=f'Игрок {player_id} бросает кубики: {dice1}, {dice2}')
        
        # Валидация входных данных
        if not (1 <= dice1 <= 6 and 1 <= dice2 <= 6):
            log.error(layer='SERVICE', component='DiceService.roll_dice', message=f'Некорректные значения кубиков: {dice1}, {dice2}')
            raise ValueError("Значения кубиков должны быть от 1 до 6")
        
        if cheat_dice_index is not None and not (0 <= cheat_dice_index <= 1):
            log.error(layer='SERVICE', component='DiceService.roll_dice', message=f'Некорректный индекс кубика: {cheat_dice_index}')
            raise ValueError("Индекс кубика должен быть 0 или 1")
        
        if cheat_dice_value is not None and not (1 <= cheat_dice_value <= 6):
            log.error(layer='SERVICE', component='DiceService.roll_dice', message=f'Некорректное значение кубика: {cheat_dice_value}')
            raise ValueError("Значение кубика должно быть от 1 до 6")
        
        player = await PlayerDAO.get_one(session, player_id)
        if not player:
            log.error(layer='SERVICE', component='DiceService.roll_dice', message=f'Игрок {player_id} не найден')
            raise ValueError("Игрок не найден")
        
        # Сохраняем предыдущую позицию
        previous_position = player.cell_id
        
        # Применяем модификаторы
        modified_dice, modifiers = await self._apply_dice_modifiers(player, dice1, dice2, 
                                                                   cheat_dice_index, cheat_dice_value)
        total_value = sum(modified_dice)
        
        # Вычисляем новую позицию
        BOARD_SIZE = 40  # 0..39
        new_position = (player.cell_id + total_value) % BOARD_SIZE
        passed_start = (player.cell_id + total_value) >= BOARD_SIZE
        
        # Сохраняем результат
        await self.player_service.update_player(player.id, {
            "last_dice_value": total_value,
            "cell_id": new_position,
            "previous_cell_id": previous_position
        })
        
        # Уменьшаем ходы эффектов
        await self.effects_service.decrement_effect_turns(player_id, session=session)
        
        result = {
            "original_dice": [dice1, dice2],
            "modified_dice": modified_dice,
            "total_value": total_value,
            "modifiers_applied": modifiers,
            "new_position": new_position,
            "passed_start": passed_start
        }
        
        log.info(layer='SERVICE', component='DiceService.roll_dice', 
                message=f'Результат броска: {result}')
        
        return result

    async def _apply_dice_modifiers(self, player: Player, dice1: int, dice2: int,
                                   cheat_dice_index: Optional[int] = None,
                                   cheat_dice_value: Optional[int] = None) -> Tuple[List[int], List[str]]:
        """
        Применяет модификаторы к значениям кубиков.
        
        Args:
            player (Player): Объект игрока с модификаторами.
            dice1 (int): Значение первого кубика.
            dice2 (int): Значение второго кубика.
            cheat_dice_index (int, optional): Индекс кубика для замены.
            cheat_dice_value (int, optional): Новое значение для кубика.
        
        Returns:
            Tuple[List[int], List[str]]: (модифицированные кубики, список примененных модификаторов)
        """
        modified_dice = [dice1, dice2]
        applied_modifiers = []
        
        # Читерский кубик - заменяет выбранное значение на заданное
        if cheat_dice_index is not None and cheat_dice_value is not None:
            modified_dice[cheat_dice_index] = cheat_dice_value
            applied_modifiers.append("cheat_dice")
            log.info(layer='SERVICE', component='DiceService._apply_dice_modifiers', 
                    message=f'Применен читерский кубик: кубик {cheat_dice_index} заменен на {cheat_dice_value}')
        
        # Кубик хуюбика - заменяет большее значение на 1
        # Проверяем через EffectsService
        effects = await self.effects_service.get_player_effects(player.id)
        huybik_effect = next((e for e in effects if e.effect_name == "Кубик хуюбика"), None)
        
        if huybik_effect:
            if modified_dice[0] > modified_dice[1]:
                modified_dice[0] = 1
            else:
                modified_dice[1] = 1
            applied_modifiers.append("huybik_dice")
            log.info(layer='SERVICE', component='DiceService._apply_dice_modifiers', 
                    message='Применен кубик хуюбика: большее значение заменено на 1')
        
        return modified_dice, applied_modifiers

    @connection
    async def get_dice_modifiers(self, player_id: UUID, session=None) -> Dict[str, Any]:
        """
        Возвращает текущие модификаторы кубиков игрока.
        
        Args:
            player_id (UUID): Идентификатор игрока.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            dict: Информация о модификаторах игрока.
        """
        player = await PlayerDAO.get_one(session, player_id)
        if not player:
            log.error(layer='SERVICE', component='DiceService.get_dice_modifiers', 
                     message=f'Игрок {player_id} не найден')
            return {"error": "Игрок не найден"}
        
        # Получаем эффекты через EffectsService
        effects = await self.effects_service.get_player_effects(player_id, session=session)
        dice_effects = [e for e in effects if e.effect_category == "DICE_MODIFIER"]
        
        modifiers = {
            "dice_effects": [{"name": e.effect_name, "turns_remaining": e.turns_remaining} for e in dice_effects],
            "total_effects": len(effects)
        }
        
        log.info(layer='SERVICE', component='DiceService.get_dice_modifiers', 
                message=f'Модификаторы игрока {player_id}: {modifiers}')
        
        return modifiers

    @connection
    async def simulate_dice_roll(self, dice1: int, dice2: int, 
                                cheat_dice_index: Optional[int] = None,
                                cheat_dice_value: Optional[int] = None,
                                player_effects: List[dict] = None) -> Dict[str, Any]:
        """
        Симулирует бросок кубиков с заданными модификаторами (без сохранения в БД).
        
        Args:
            dice1 (int): Значение первого кубика (1-6).
            dice2 (int): Значение второго кубика (1-6).
            cheat_dice_index (int, optional): Индекс кубика для замены.
            cheat_dice_value (int, optional): Новое значение для кубика.
            player_effects (List[dict], optional): Список эффектов игрока.
        
        Returns:
            dict: Результат симуляции броска.
        """
        if not (1 <= dice1 <= 6 and 1 <= dice2 <= 6):
            raise ValueError("Значения кубиков должны быть от 1 до 6")
        
        # Создаем временный объект игрока для симуляции
        class MockPlayer:
            def __init__(self):
                self.id = None
        
        mock_player = MockPlayer()
        
        # Применяем модификаторы
        modified_dice, modifiers = await self._apply_dice_modifiers(mock_player, dice1, dice2,
                                                                   cheat_dice_index, cheat_dice_value)
        total_value = sum(modified_dice)
        
        result = {
            "original_dice": [dice1, dice2],
            "modified_dice": modified_dice,
            "total_value": total_value,
            "modifiers_applied": modifiers
        }
        
        log.info(layer='SERVICE', component='DiceService.simulate_dice_roll', 
                message=f'Симуляция броска: {result}')
        
        return result 