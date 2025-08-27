from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from src.database.postgres.dao.dao import InventoryDAO, ItemInstanceDAO, ItemDAO, PlayerDAO
from src.services.base_service import BaseService
from src.services.item_instance_service import ItemInstanceService
from src.schemas.inventory import InventoryCreate, InventoryResponse, InventoryWithItems
from src.schemas.item_instance import ItemInstanceCreate, ItemInstanceUpdate, ItemInstanceResponse, ItemInstanceWithItem
from src.schemas.item import ItemResponse
from src.database.postgres.dao.base import connection
from src.utils.logger import log
from src.services.effects_service import EffectsService
from src.schemas import ServiceResult


class InventoryService(BaseService):
    """Сервис для работы с инвентарем, предметами и игроками"""
    
    def __init__(self):
        super().__init__(InventoryDAO)
        self.item_instance_service = ItemInstanceService()
    
    @connection
    async def add_item_to_inventory(self, inventory_id: int, item_id: int, uses: int = 1, modifier_turns: int = None, session=None) -> ServiceResult[ItemInstanceResponse]:
        """
        Добавляет новый экземпляр предмета (ItemInstance) в инвентарь игрока.
        Проверяет заполненность инвентаря, создает экземпляр предмета, вызывает on_acquire-логику предмета.
        
        Args:
            inventory_id (int): Идентификатор инвентаря, куда добавляется предмет.
            item_id (int): Идентификатор предмета (Item).
            uses (int, optional): Количество использований предмета. По умолчанию 1.
            modifier_turns (int, optional): Количество ходов действия модификатора (если применимо).
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[ItemInstanceResponse]: Результат добавления экземпляра предмета.
        
        Raises:
            ValueError: Если инвентарь заполнен или другие ошибки создания.
        """
        try:
            log.info(layer='SERVICE', component='InventoryService.add_item_to_inventory', message=f'Добавление предмета {item_id} в инвентарь {inventory_id}')
            item_instance = await InventoryDAO.add_item_to_inventory(session, {
                "inventory_id": inventory_id,
                "item_id": item_id,
                "uses": uses,
                "modifier_turns": modifier_turns
            })
            
            # Вызываем on_acquire логику предмета
            item = await ItemDAO.get_one(session, item_id)
            if item:
                await self.item_instance_service._on_acquire_item(item.title, item_instance, inventory_id, session)
            
            log.info(layer='SERVICE', component='InventoryService.add_item_to_inventory', message=f'Успешно добавлен экземпляр предмета {item_id} в инвентарь {inventory_id}')
            return ServiceResult(success=True, data=ItemInstanceResponse.model_validate(item_instance))
        except ValueError as e:
            log.error(layer='SERVICE', component='InventoryService.add_item_to_inventory', message=f'Ошибка: {e}')
            return ServiceResult(success=False, message=str(e))
    
    @connection
    async def remove_item_from_inventory(self, item_instance_id: int, session=None) -> ServiceResult[str]:
        """
        Удаляет экземпляр предмета (ItemInstance) из инвентаря по его идентификатору.
        
        Args:
            item_instance_id (int): Идентификатор экземпляра предмета для удаления.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[str]: Результат удаления экземпляра предмета.
        """
        item_instance = await ItemInstanceDAO.get_one(session, item_instance_id)
        if not item_instance:
            log.error(layer='SERVICE', component='InventoryService.remove_item_from_inventory', message=f'Экземпляр предмета {item_instance_id} не найден')
            return ServiceResult(success=False, message="Экземпляр предмета не найден")
        
        # Удаляем эффекты связанные с этим предметом
        effects_service = EffectsService()
        await effects_service.remove_effects_by_item_instance(item_instance_id, session=session)
        
        # Удаляем предмет
        await ItemInstanceDAO.delete_one(session, item_instance_id)
        log.info(layer='SERVICE', component='InventoryService.remove_item_from_inventory', message=f'Экземпляр предмета {item_instance_id} удален из инвентаря')
        return ServiceResult(success=True, data="Предмет удален из инвентаря")
    
    @connection
    async def use_item(self, item_instance_id: int, player_id: UUID, target_player_id: Optional[UUID] = None, session=None, **kwargs) -> ServiceResult[Dict[str, Any]]:
        """
        Использует предмет (ItemInstance) из инвентаря игрока. Выполняет игровую логику предмета, вызывает специальные эффекты, взаимодействует с другими игроками.
        
        Args:
            item_instance_id (int): Идентификатор экземпляра предмета.
            player_id (UUID): Идентификатор игрока, использующего предмет.
            target_player_id (UUID, optional): Идентификатор целевого игрока (если предмет требует).
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
            **kwargs: Дополнительные параметры для логики предмета.
        
        Returns:
            ServiceResult[dict]: Результат использования предмета.
        """
        log.info(layer='SERVICE', component='InventoryService.use_item', message=f'Игрок {player_id} использует предмет {item_instance_id}')
        
        # Получаем игрока
        player = await PlayerDAO.get_one(session, player_id)
        if not player:
            log.error(layer='SERVICE', component='InventoryService.use_item', message=f'Игрок {player_id} не найден')
            return ServiceResult(success=False, message="Игрок не найден")
        
        # Получаем экземпляр предмета
        item_instance = await ItemInstanceDAO.get_one(session, item_instance_id)
        if not item_instance:
            return ServiceResult(success=False, message="Предмет не найден")
        
        # Проверяем, что предмет принадлежит игроку
        if item_instance.inventory_id != player.inventory_id:
            return ServiceResult(success=False, message="Предмет не принадлежит игроку")
        
        # Получаем целевого игрока если указан
        target_player = None
        if target_player_id:
            target_player = await PlayerDAO.get_one(session, target_player_id)
        
        # Проверяем конфликты эффектов
        conflicts = await self.item_instance_service._check_effect_conflicts(player, session=session)
        if conflicts.get("has_conflicts"):
            await self.item_instance_service._resolve_effect_conflicts(player, session=session)
        
        # Используем предмет по названию
        result = await self.item_instance_service._use_item_by_title(
            item_instance.item.title, 
            item_instance, 
            player, 
            target_player, 
            session, 
            **kwargs
        )
        
        # Проверяем специальные взаимодействия между предметами
        await self.item_instance_service._check_item_interactions(session, player)
        
        log.info(layer='SERVICE', component='InventoryService.use_item', message=f'Результат использования предмета {item_instance_id}: {result}')
        return ServiceResult(success=True, data=result)
    
    @connection
    async def get_item_instance_with_item(self, item_instance_id: int, session=None) -> ServiceResult[Optional[ItemInstanceWithItem]]:
        """
        Возвращает экземпляр предмета (ItemInstance) с вложенными данными предмета (Item).
        Использует жадную загрузку (joinedload) для получения связанных данных.
        
        Args:
            item_instance_id (int): Идентификатор экземпляра предмета.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[ItemInstanceWithItem | None]: Результат получения экземпляра предмета.
        """
        query = select(ItemInstance).options(joinedload(ItemInstance.item)).where(ItemInstance.id == item_instance_id)
        result = await session.execute(query)
        item_instance = result.scalar_one_or_none()
        if not item_instance:
            log.error(layer='SERVICE', component='InventoryService.get_item_instance_with_item', message=f'Экземпляр предмета {item_instance_id} не найден')
            return ServiceResult(success=False, message="Экземпляр предмета не найден")
        log.info(layer='SERVICE', component='InventoryService.get_item_instance_with_item', message=f'Экземпляр предмета {item_instance_id} успешно получен с данными предмета')
        return ServiceResult(success=True, data=ItemInstanceWithItem.model_validate(item_instance))
    
    @connection
    async def update_item_instance(self, item_instance_id: int, update_data: ItemInstanceUpdate, session=None) -> ServiceResult[Optional[ItemInstanceResponse]]:
        """
        Обновляет данные экземпляра предмета (ItemInstance) по его идентификатору.
        
        Args:
            item_instance_id (int): Идентификатор экземпляра предмета.
            update_data (ItemInstanceUpdate): Данные для обновления (uses, modifier_turns и др.).
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[ItemInstanceResponse | None]: Результат обновления экземпляра предмета.
        """
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict['id'] = item_instance_id
        log.info(layer='SERVICE', component='InventoryService.update_item_instance', message=f'Обновление экземпляра предмета {item_instance_id} с данными {update_dict}')
        item_instance = await ItemInstanceDAO.update_one(session, update_dict)
        if not item_instance:
            log.error(layer='SERVICE', component='InventoryService.update_item_instance', message=f'Экземпляр предмета {item_instance_id} не найден для обновления')
            return ServiceResult(success=False, message="Экземпляр предмета не найден для обновления")
        log.info(layer='SERVICE', component='InventoryService.update_item_instance', message=f'Экземпляр предмета {item_instance_id} успешно обновлен')
        return ServiceResult(success=True, data=ItemInstanceResponse.model_validate(item_instance))
    
    @connection
    async def get_inventory_by_player_id(self, player_id: UUID, session=None) -> ServiceResult[Optional[InventoryWithItems]]:
        """
        Возвращает инвентарь игрока (Inventory) по идентификатору игрока, включая все предметы в инвентаре.
        
        Args:
            player_id (UUID): Идентификатор игрока.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[InventoryWithItems | None]: Результат получения инвентаря.
        """
        player = await PlayerDAO.get_one(session, player_id)
        if not player:
            log.error(layer='SERVICE', component='InventoryService.get_inventory_by_player_id', message=f'Игрок {player_id} не найден')
            return ServiceResult(success=False, message="Игрок не найден")
        log.info(layer='SERVICE', component='InventoryService.get_inventory_by_player_id', message=f'Получение инвентаря игрока {player_id}')
        return ServiceResult(success=True, data=await self.get_inventory_with_items(player.inventory_id, session))
    
    @connection
    async def search_items_in_inventory(self, inventory_id: int, item_name: str = None, session=None) -> ServiceResult[List[ItemInstanceWithItem]]:
        """
        Выполняет поиск предметов в инвентаре по названию предмета (Item.title) или возвращает все предметы инвентаря.
        Возвращает расширенную схему с вложенными данными предмета.
        
        Args:
            inventory_id (int): Идентификатор инвентаря.
            item_name (str, optional): Название предмета для поиска (поиск по подстроке, регистронезависимо).
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[List[ItemInstanceWithItem]]: Результат поиска предметов.
        """
        items = await self.dao.search_items_in_inventory(session, inventory_id, item_name)
        log.info(layer='SERVICE', component='InventoryService.search_items_in_inventory', message=f'Поиск предметов в инвентаре {inventory_id} по названию "{item_name}". Найдено: {len(items)}')
        return ServiceResult(success=True, data=[ItemInstanceWithItem.model_validate(item) for item in items])
    
    @connection
    async def get_inventory_stats(self, inventory_id: int, session=None) -> ServiceResult[Dict[str, Any]]:
        """
        Возвращает статистику по инвентарю: количество предметов, общее число использований, уникальных предметов и среднее число использований на предмет.
        
        Args:
            inventory_id (int): Идентификатор инвентаря.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[dict]: Статистика инвентаря.
        """
        items = await ItemInstanceDAO.find_by(session, inventory_id=inventory_id)
        
        total_items = len(items)
        total_uses = sum(item.uses for item in items)
        unique_items = len(set(item.item_id for item in items))
        
        log.info(layer='SERVICE', component='InventoryService.get_inventory_stats', message=f'Статистика инвентаря {inventory_id}: total_items={total_items}, total_uses={total_uses}, unique_items={unique_items}')
        return ServiceResult(success=True, data={
            'total_items': total_items,
            'total_uses': total_uses,
            'unique_items': unique_items,
            'average_uses_per_item': total_uses / total_items if total_items > 0 else 0
        })
    
    @connection
    async def transfer_item(self, from_inventory_id: int, to_inventory_id: int, item_instance_id: int, session=None) -> ServiceResult[bool]:
        """
        Перемещает экземпляр предмета из одного инвентаря в другой. Проверяет наличие предмета, целевого инвентаря и заполненность целевого инвентаря.
        
        Args:
            from_inventory_id (int): Идентификатор исходного инвентаря.
            to_inventory_id (int): Идентификатор целевого инвентаря.
            item_instance_id (int): Идентификатор экземпляра предмета.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[bool]: Результат передачи экземпляра предмета.
        """
        item_instance = await ItemInstanceDAO.get_one(session, item_instance_id)
        if not item_instance or item_instance.inventory_id != from_inventory_id:
            log.error(layer='SERVICE', component='InventoryService.transfer_item', message=f'Экземпляр предмета {item_instance_id} не найден в инвентаре {from_inventory_id}')
            return ServiceResult(success=False, message="Экземпляр предмета не найден в исходном инвентаре")
        
        target_inventory = await self.get_by_id(to_inventory_id, session)
        if not target_inventory:
            log.error(layer='SERVICE', component='InventoryService.transfer_item', message=f'Целевой инвентарь {to_inventory_id} не найден')
            return ServiceResult(success=False, message="Целевой инвентарь не найден")
        
        if await self.dao.is_inventory_full(session, to_inventory_id):
            log.error(layer='SERVICE', component='InventoryService.transfer_item', message=f'Целевой инвентарь {to_inventory_id} переполнен')
            return ServiceResult(success=False, message="Целевой инвентарь переполнен")
        
        await ItemInstanceDAO.update_one(session, {
            'id': item_instance_id,
            'inventory_id': to_inventory_id
        })
        
        log.info(layer='SERVICE', component='InventoryService.transfer_item', message=f'Экземпляр предмета {item_instance_id} перемещен из инвентаря {from_inventory_id} в {to_inventory_id}')
        return ServiceResult(success=True, data=True)
    
    @connection
    async def get_inventory_items_count(self, inventory_id: int, session=None) -> ServiceResult[int]:
        """
        Возвращает количество предметов в инвентаре по его идентификатору.
        
        Args:
            inventory_id (int): Идентификатор инвентаря.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[int]: Количество предметов в инвентаре.
        """
        count = await self.dao.count(session, inventory_id=inventory_id)
        log.info(layer='SERVICE', component='InventoryService.get_inventory_items_count', message=f'В инвентаре {inventory_id} {count} предметов')
        return ServiceResult(success=True, data=count)
    
    @connection
    async def is_inventory_full(self, inventory_id: int, session=None) -> ServiceResult[bool]:
        """
        Проверяет, заполнен ли инвентарь (максимум 6 предметов).
        
        Args:
            inventory_id (int): Идентификатор инвентаря.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[bool]: Результат проверки заполненности инвентаря.
        """
        full = await self.dao.is_inventory_full(session, inventory_id)
        log.info(layer='SERVICE', component='InventoryService.is_inventory_full', message=f'Проверка заполненности инвентаря {inventory_id}: {full}')
        return ServiceResult(success=True, data=full)

    @connection
    async def get_inventory_items(self, player_id: UUID, session=None) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Возвращает список всех предметов в инвентаре игрока по его идентификатору.
        
        Args:
            player_id (UUID): Идентификатор игрока.
            session: Асинхронная сессия SQLAlchemy (автоматически подставляется декоратором).
        
        Returns:
            ServiceResult[List[dict]]: Список словарей с данными предметов.
        """
        player = await PlayerDAO.get_one(session, player_id)
        if not player:
            log.error(layer='SERVICE', component='InventoryService.get_inventory_items', message=f'Игрок {player_id} не найден')
            return ServiceResult(success=False, message="Игрок не найден")
        
        items = await InventoryDAO.search_items_in_inventory(session, player.inventory_id)
        log.info(layer='SERVICE', component='InventoryService.get_inventory_items', message=f'Получено {len(items)} предметов для игрока {player_id}')
        return ServiceResult(success=True, data=[
            {
                "id": item.id,
                "title": item.item.title,
                "description": item.item.description,
                "type": item.item.type,
                "uses": item.uses,
                "modifier_turns": item.modifier_turns
            }
            for item in items
        ])
