from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.postgres.dao.dao import ItemInstanceDAO, PlayerDAO, InventoryDAO, ItemDAO
from src.database.postgres.models import ItemInstance, Item, Player
from src.database.postgres.sql_enums import ItemType, EffectType, EffectCategory
from src.services.base_service import BaseService
from src.services.player_service import PlayerService
from src.services.cell_service import CellService
from src.services.game_service import GameService
from src.services.effects_service import EffectsService
from src.utils.logger import log
from src.database.postgres.dao.base import connection
from src.schemas import ServiceResult
from src.schemas.item_instance import ItemInstanceResponse


class ItemInstanceService(BaseService):
    """Сервис для работы с экземплярами предметов и их логикой"""
    
    def __init__(self):
        super().__init__(ItemInstanceDAO)
        self.player_service = PlayerService()
        self.cell_service = CellService()
        self.game_service = GameService()
        self.effects_service = EffectsService()

    # ==================== ЛОГИКА ПРЕДМЕТОВ ==================== #

    # 1. Читерский кубик
    async def _use_cheat_dice(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        new_dice_value = kwargs.get('new_dice_value')
        if not new_dice_value:
            return {"success": False, "message": "Не указано новое значение кубика"}
        
        await self.player_service.update_player(player.id, {"dice_modifier": new_dice_value})
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": f"Значение кубика изменено на {new_dice_value}"}

    # 2. Кубик хуюбика
    async def _use_huybik_dice(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        await self.player_service.update_player(player.id, {"dice_modifier": 1, "game_modifier": "huybik_dice"})
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": "При следующем броске большее значение кубика будет заменено на 1"}

    # 3. Очки EZ
    async def _use_ez_glasses(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="ez_difficulty",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=2,
            session=session
        )
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "Следующие 2 хода игры будут на легком уровне сложности"}

    # 4. Повязка Рэмбо
    async def _use_rambo_bandana(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="rambo_difficulty",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=2,
            session=session
        )
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "Следующие 2 хода игры будут на высоком уровне сложности"}

    # 5. Свиток реролла
    async def _use_reroll_scroll(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        game_id = kwargs.get('game_id')
        if not game_id:
            return {"success": False, "message": "Не указан ID игры для реролла"}
        
        result = await self.game_service.reroll_game(game_id)
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": "Игра перезапущена", "game_data": result}

    # 6. Шар всезнания
    async def _use_knowledge_sphere(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        # Эффект сохраняется до конца хода, просто используем предмет
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": "Предмет использован, эффект будет удален в конце хода"}

    # 7. Взрывчатка
    async def _use_explosive(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        coin_side = kwargs.get('coin_side')
        if not coin_side:
            return {"success": False, "message": "Не указана сторона монетки"}
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        if coin_side == 'heads':
            return {"success": True, "message": "Эффект сработал", "effect_active": True}
        else:
            return {"success": True, "message": "Эффект не сработал", "effect_active": False}

    # 8. Корона колесного короля
    async def _use_wheel_crown(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        selected_game = kwargs.get('selected_game')
        if not selected_game:
            return {"success": False, "message": "Не выбрана игра"}
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": f"Выбрана игра: {selected_game}", "selected_game": selected_game}

    # 9. Ремонтный набор
    async def _use_repair_kit(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        target_item_id = kwargs.get('target_item_id')
        if not target_item_id:
            return {"success": False, "message": "Не указан предмет для ремонта"}
        
        target_item = await ItemInstanceDAO.get_one(session, target_item_id)
        if not target_item or target_item.inventory_id != player.inventory_id:
            return {"success": False, "message": "Предмет не найден в инвентаре"}
        
        await ItemInstanceDAO.update_one(session, {
            'id': target_item_id,
            'uses': target_item.uses + 1
        })
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "Заряды предмета увеличены на 1"}

    # 10. Красочная манга
    async def _use_colorful_manga(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        # Эффект сохраняется до конца хода, просто используем предмет
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": "Предмет использован, эффект будет удален в конце хода"}

    # 11. Рука мидаса
    async def _use_midas_hand(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        wheel_item = kwargs.get('wheel_item')
        if not wheel_item:
            return {"success": False, "message": "Не указан предмет с колеса"}
        
        # Здесь должна быть логика добавления очков
        # await PlayerStatsDAO.increment_stats(session, {"player_id": player.id, "total_points": 2})
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": f"Предмет '{wheel_item}' обменян на 2 очка", "points_gained": 2}

    # 12. Реверсивные сапоги
    async def _use_reverse_boots(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        dice_value = kwargs.get('dice_value')
        if not dice_value:
            return {"success": False, "message": "Не указано значение кубика"}
        
        new_cell_id = max(0, player.cell_id - dice_value)
        await self.player_service.update_player(player.id, {"cell_id": new_cell_id})
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": f"Возвращены назад на {dice_value} клеток, новая позиция: {new_cell_id}"}

    # 13. Парные кольца времени
    async def _use_time_rings(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        if not target_player:
            return {"success": False, "message": "Не указан целевой игрок"}
        
        await InventoryDAO.add_item_to_inventory(session, {
            "inventory_id": target_player.inventory_id,
            "item_id": item_instance.item_id,
            "uses": item_instance.uses,
            "modifier_turns": None
        })
        
        await ItemInstanceDAO.update_one(session, {
            'id': item_instance.id,
            'modifier_turns': None
        })
        
        return {"success": True, "message": f"Кольцо времени связано с игроком {target_player.username}"}

    # 14. Тухлая шаурма (ловушка)
    async def _use_rotten_shawarma(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        if not target_player:
            return {"success": False, "message": "Не указан целевой игрок"}
        
        await self.effects_service.add_player_effect(
            player_id=target_player.id,
            effect_name="rotten_shawarma",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.MOVEMENT,
            turns_remaining=2,
            effect_data={"dice_penalty": 1},
            session=session
        )
        
        await ItemInstanceDAO.delete_one(session, item_instance.id)
        return {"success": True, "message": f"Ловушка применена к игроку {target_player.username}: -1 к кубикам на 2 хода"}

    # 15. Четырехлистный клевер
    async def _use_lucky_clover(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        use_type = kwargs.get('use_type')
        
        if use_type == 'block_trap':
            trap_item_id = kwargs.get('trap_item_id')
            if not trap_item_id:
                return {"success": False, "message": "Не указана ловушка для отбивания"}
            
            await ItemInstanceDAO.delete_one(session, trap_item_id)
            await ItemInstanceDAO.use_item(session, item_instance.id)
            return {"success": True, "message": "Ловушка отбита"}
        
        elif use_type == 'auction_bonus':
            bonus_type = kwargs.get('bonus_type')
            
            if bonus_type == 'points':
                # await PlayerStatsDAO.increment_stats(session, {"player_id": player.id, "total_points": 2})
                await ItemInstanceDAO.use_item(session, item_instance.id)
                return {"success": True, "message": "Получено +2 очка за прохождение игры"}
            
            elif bonus_type == 'easy_difficulty':
                await self.effects_service.add_player_effect(
                    player_id=player.id,
                    effect_name="easy_difficulty",
                    effect_type=EffectType.BUFF,
                    effect_category=EffectCategory.GAME_MODIFIER,
                    turns_remaining=1,
                    session=session
                )
                await ItemInstanceDAO.use_item(session, item_instance.id)
                return {"success": True, "message": "Игра будет пройдена на легком уровне сложности"}
        
        return {"success": False, "message": "Неверный тип использования клевера"}

    # 16. Чокер боли (ловушка)
    async def _use_pain_choker(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        if not target_player:
            return {"success": False, "message": "Не указан целевой игрок"}
        
        await self.effects_service.add_player_effect(
            player_id=target_player.id,
            effect_name="pain_choker",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=1,
            effect_data={"genre_rules_only": True},
            session=session
        )
        
        await ItemInstanceDAO.delete_one(session, item_instance.id)
        return {"success": True, "message": f"Ловушка применена к игроку {target_player.username}: следующая игра только по жанровым правилам"}

    # 17. Полукаловая монетка (ловушка)
    async def _use_half_penny(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        if not target_player:
            return {"success": False, "message": "Не указан целевой игрок"}
        
        await self.effects_service.add_player_effect(
            player_id=target_player.id,
            effect_name="half_penny",
            effect_type=EffectType.NEUTRAL,
            effect_category=EffectCategory.TIME_MODIFIER,
            turns_remaining=1,
            effect_data={"coin_flip": True},
            session=session
        )
        
        await ItemInstanceDAO.delete_one(session, item_instance.id)
        return {"success": True, "message": f"Ловушка применена к игроку {target_player.username}: на следующей клетке с временем подбрасывается монетка"}

    # 18. Шоколад
    async def _use_chocolate(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        cell_id = kwargs.get('cell_id')
        if not cell_id:
            return {"success": False, "message": "Не указана клетка для применения эффекта"}
        
        cell = await self.cell_service.get_cell(cell_id)
        if not cell:
            return {"success": False, "message": "Клетка не найдена"}
        
        new_min_time = max(1, cell.min_time - 1)
        new_max_time = max(new_min_time + 1, cell.max_time - 1)
        
        await self.cell_service.update_cell(cell_id, {
            "min_time": new_min_time,
            "max_time": new_max_time
        })
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": f"Время на клетке уменьшено: {new_min_time}-{new_max_time} часов"}

    async def _on_acquire_item(self, title: str, item_instance: ItemInstance, inventory_id: int, session=None) -> Dict[str, Any]:
        """Делегирование on_acquire по названию предмета"""
        handlers = {
            "Шоколад": self._on_acquire_chocolate,
            "Шар всезнания": self._on_acquire_knowledge_sphere,
            "Красочная манга": self._on_acquire_colorful_manga,
        }
        handler = handlers.get(title)
        if handler:
            return await handler(item_instance, inventory_id, session)
        return {"success": True, "message": "Предмет получен"}

    async def _on_acquire_chocolate(self, item_instance: ItemInstance, inventory_id: int, session=None) -> Dict[str, Any]:
        items = await InventoryDAO.search_items_in_inventory(session, inventory_id)
        chocolate_items = [item for item in items if item.item.title == "Шоколад"]
        if len(chocolate_items) >= 4:
            total_uses = sum(item.uses for item in chocolate_items)
            for item in chocolate_items:
                await ItemInstanceDAO.delete_one(session, item.id)
            await InventoryDAO.add_item_to_inventory(session, {
                "inventory_id": inventory_id,
                "item_id": item_instance.item_id,
                "uses": 1,
                "modifier_turns": None
            })
            return {"success": True, "message": "4 шоколада превращены в плитку шоколада"}
        return {"success": True, "message": "Шоколад добавлен в инвентарь"}

    async def _on_acquire_knowledge_sphere(self, item_instance: ItemInstance, inventory_id: int, session=None) -> Dict[str, Any]:
        # Получаем игрока по inventory_id
        player = await PlayerDAO.find_one_by(session, inventory_id=inventory_id)
        if player:
                    await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="allow_guide",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=None,  # Бесконечный эффект
            item_instance_id=item_instance.id,
            session=session
        )
        return {"success": True, "message": "Шар всезнания добавлен в инвентарь, разрешено использование гайда"}

    async def _on_acquire_colorful_manga(self, item_instance: ItemInstance, inventory_id: int, session=None) -> Dict[str, Any]:
        # Получаем игрока по inventory_id
        player = await PlayerDAO.find_one_by(session, inventory_id=inventory_id)
        if player:
            await self.effects_service.add_player_effect(
                player_id=player.id,
                effect_name="visual_novel_no_skip",
                effect_type=EffectType.BUFF,
                effect_category=EffectCategory.GAME_MODIFIER,
                turns_remaining=None,  # Бесконечный эффект
                item_instance_id=item_instance.id,
                session=session
            )
        return {"success": True, "message": "Красочная манга добавлена в инвентарь, запрещен автоскип в визуальных новеллах"}

    # 19. Туалетка
    async def _use_toilet_paper(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        previous_cell_id = kwargs.get('previous_cell_id')
        if not previous_cell_id:
            return {"success": False, "message": "Не указана предыдущая клетка"}
        
        await self.player_service.update_player(player.id, {"cell_id": previous_cell_id})
        await ItemInstanceDAO.use_item(session, item_instance.id)
        
        return {"success": True, "message": f"Возвращены на клетку {previous_cell_id} вместо тюрьмы"}

    # 20. Штрафная квитанция
    async def _use_penalty_receipt(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="penalty_receipt",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.TIME_MODIFIER,
            turns_remaining=1,
            effect_data={"time_increase": 3},
            session=session
        )
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "На следующей клетке с временем время будет увеличено на 3 часа"}

    # 21. Дырявый парашют
    async def _use_parachute(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        await self.player_service.update_player(player.id, {"cell_id": 0})
        
        # await PlayerStatsDAO.increment_stats(session, {"player_id": player.id, "total_points": -2})
        
        await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="no_points_next_game",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=1,
            session=session
        )
        
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "Перемещены на старт, потеряно 2 очка, следующая игра не принесет очков"}

    # 22. Наперсток удачи
    async def _use_lucky_thimble(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        unwanted_item = kwargs.get('unwanted_item')
        desired_item = kwargs.get('desired_item')
        
        if not unwanted_item or not desired_item:
            return {"success": False, "message": "Не указаны предметы для замены"}
        
        return {"success": True, "message": f"Пункт '{unwanted_item}' заменен на '{desired_item}'"}

    # 23. Рука для fisting
    async def _use_fisting_hand(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        if not target_player:
            return {"success": False, "message": "Не указан целевой игрок"}
        
        await InventoryDAO.add_item_to_inventory(session, {
            "inventory_id": target_player.inventory_id,
            "item_id": item_instance.item_id,
            "uses": item_instance.uses,
            "modifier_turns": item_instance.modifier_turns
        })
        
        await ItemInstanceDAO.update_one(session, {
            'id': item_instance.id,
            'modifier_turns': item_instance.modifier_turns
        })
        
        return {"success": True, "message": f"Игрок {target_player.username} стал вашим рабом"}

    # 24. Тотем мошны
    async def _use_mohsna_totem(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="trap_protection",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.PROTECTION,
            turns_remaining=2,
            session=session
        )
        
        return {"success": True, "message": "Защита от ловушек-событий активирована на 2 хода"}

    # 25. Плюсовый блокнот
    async def _use_plus_notebook(self, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        dice_values = kwargs.get('dice_values', [])
        
        if len(dice_values) == 2 and dice_values[0] == dice_values[1]:
            if dice_values[0] == 6:
                # await PlayerStatsDAO.increment_stats(session, {"player_id": player.id, "total_points": 1})
                return {"success": True, "message": "Выпали две шестерки! Получено +1 очко", "bonus_points": 1}
            else:
                return {"success": True, "message": f"Выпали одинаковые значения! +2 к движению", "movement_bonus": 2}
        
        return {"success": True, "message": "Обычный бросок кубиков"}

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    async def _use_item_by_title(self, title: str, item_instance: ItemInstance, player: Player, target_player: Optional[Player] = None, session=None, **kwargs) -> Dict[str, Any]:
        """Делегирование использования по названию предмета"""
        handlers = {
            "Читерский кубик": self._use_cheat_dice,
            "Кубик хуюбика": self._use_huybik_dice,
            "Очки EZ": self._use_ez_glasses,
            "Повязка Рэмбо": self._use_rambo_bandana,
            "Свиток реролла": self._use_reroll_scroll,
            "Шар всезнания": self._use_knowledge_sphere,
            "Взрывчатка": self._use_explosive,
            "Корона колесного короля": self._use_wheel_crown,
            "Ремонтный набор": self._use_repair_kit,
            "Красочная манга": self._use_colorful_manga,
            "Рука мидаса": self._use_midas_hand,
            "Реверсивные сапоги": self._use_reverse_boots,
            "Парные кольца времени": self._use_time_rings,
            "Тухлая шаурма": self._use_rotten_shawarma,
            "Четырехлистный клевер": self._use_lucky_clover,
            "Чокер боли": self._use_pain_choker,
            "Полукаловая монетка": self._use_half_penny,
            "Шоколад": self._use_chocolate,
            "Туалетка": self._use_toilet_paper,
            "Штрафная квитанция": self._use_penalty_receipt,
            "Дырявый парашют": self._use_parachute,
            "Наперсток удачи": self._use_lucky_thimble,
            "Рука для fisting": self._use_fisting_hand,
            "Тотем мошны": self._use_mohsna_totem,
            "Плюсовый блокнот": self._use_plus_notebook,
        }
        
        handler = handlers.get(title)
        if handler:
            return await handler(item_instance, player, target_player, session, **kwargs)
        return {"success": False, "message": f"Обработчик для предмета '{title}' не найден"}

    async def _check_item_interactions(self, session: AsyncSession, player: Player):
        """Проверка специальных взаимодействий между предметами"""
        items = await InventoryDAO.search_items_in_inventory(session, player.inventory_id)
        
        # Читерский кубик + Кубик хуюбика
        cheat_dice = None
        huybik_dice = None
        
        for item in items:
            if item.item.title == "Читерский кубик":
                cheat_dice = item
            elif item.item.title == "Кубик хуюбика":
                huybik_dice = item
        
        if cheat_dice and huybik_dice:
            await ItemInstanceDAO.delete_one(session, cheat_dice.id)
            await ItemInstanceDAO.delete_one(session, huybik_dice.id)
            log.info(f"Предметы 'Читерский кубик' и 'Кубик хуюбика' уничтожены у игрока {player.username}")
        
        # Очки EZ + Повязка Рэмбо
        ez_glasses = None
        rambo_bandana = None
        
        for item in items:
            if item.item.title == "Очки EZ":
                ez_glasses = item
            elif item.item.title == "Повязка Рэмбо":
                rambo_bandana = item
        
        if ez_glasses and rambo_bandana:
            await ItemInstanceDAO.delete_one(session, ez_glasses.id)
            await ItemInstanceDAO.delete_one(session, rambo_bandana.id)
            log.info(f"Предметы 'Очки EZ' и 'Повязка Рэмбо' уничтожены у игрока {player.username}")

    async def _check_effect_conflicts(self, player: Player, session=None) -> Dict[str, Any]:
        """
        Проверяет конфликты эффектов у игрока и разрешает их.
        
        Args:
            player (Player): Игрок
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            dict: Результат проверки конфликтов
        """
        return await self.effects_service.check_effect_conflicts(player.id, session=session)

    async def _resolve_effect_conflicts(self, player: Player, session=None) -> Dict[str, Any]:
        """
        Разрешает конфликты эффектов у игрока.
        
        Args:
            player (Player): Игрок
            session: Асинхронная сессия SQLAlchemy
        
        Returns:
            dict: Результат разрешения конфликтов
        """
        return await self.effects_service.resolve_effect_conflicts(player.id, session=session)

    # ==================== ОСНОВНЫЕ МЕТОДЫ ====================
