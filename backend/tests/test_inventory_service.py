import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.inventory_service import InventoryService
from src.schemas.inventory import InventoryCreate, InventoryResponse, InventoryWithItems
from src.schemas.item_instance import ItemInstanceCreate, ItemInstanceResponse
from src.schemas.item import ItemResponse
from src.database.postgres.sql_enums import ItemType
from src.schemas import ServiceResult


class TestInventoryService:
    """Тесты для InventoryService по паттерну AAA (Arrange, Act, Assert)"""

    @pytest.fixture
    def inventory_service(self):
        """Создание экземпляра InventoryService для тестирования."""
        return InventoryService()

    @pytest.fixture
    def sample_inventory(self):
        """Тестовые данные инвентаря."""
        return MagicMock(
            id=1,
            player_id=uuid4()
        )

    @pytest.fixture
    def sample_item(self):
        """Тестовые данные предмета."""
        return MagicMock(
            id=1,
            title="Читерский кубик",
            description="Позволяет заменить значение кубика",
            item_image="cheat_dice.png",
            type=ItemType.MODIFIER,
            uses=None,
            modifier_turns=None
        )

    @pytest.fixture
    def sample_item_instance(self):
        """Тестовые данные экземпляра предмета."""
        return MagicMock(
            id=1,
            item_id=1,
            inventory_id=1,
            uses=3,
            modifier_turns=None
        )

    @pytest.mark.asyncio
    async def test_add_item_to_inventory_success(self, inventory_service, sample_item_instance, sample_item):
        """Тест успешного добавления предмета в инвентарь."""
        # Arrange
        inventory_id = 1
        item_id = 1
        uses = 3
        modifier_turns = None
        
        inventory_service.dao.add_item_to_inventory = AsyncMock(return_value=sample_item_instance)
        inventory_service.dao.get_one = AsyncMock(return_value=sample_item)
        inventory_service.item_instance_service._on_acquire_item = AsyncMock()
        
        # Act
        result = await inventory_service.add_item_to_inventory(inventory_id, item_id, uses, modifier_turns, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert isinstance(result.data, ItemInstanceResponse)
        assert result.data.id == sample_item_instance.id
        inventory_service.dao.add_item_to_inventory.assert_called_once_with(
            None, {
                "inventory_id": inventory_id,
                "item_id": item_id,
                "uses": uses,
                "modifier_turns": modifier_turns
            }
        )
        inventory_service.dao.get_one.assert_called_once_with(None, item_id)
        inventory_service.item_instance_service._on_acquire_item.assert_called_once_with(
            sample_item.title, sample_item_instance, inventory_id, None
        )

    @pytest.mark.asyncio
    async def test_add_item_to_inventory_inventory_full(self, inventory_service):
        """Тест добавления предмета в заполненный инвентарь."""
        # Arrange
        inventory_id = 1
        item_id = 1
        
        inventory_service.dao.add_item_to_inventory = AsyncMock(side_effect=ValueError("Inventory is full"))
        
        # Act
        result = await inventory_service.add_item_to_inventory(inventory_id, item_id, 1, None, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        assert "Inventory is full" in result.message
        inventory_service.dao.add_item_to_inventory.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_item_to_inventory_item_not_found(self, inventory_service, sample_item_instance):
        """Тест добавления несуществующего предмета в инвентарь."""
        # Arrange
        inventory_id = 1
        item_id = 999
        
        inventory_service.dao.add_item_to_inventory = AsyncMock(return_value=sample_item_instance)
        inventory_service.dao.get_one = AsyncMock(return_value=None)
        inventory_service.item_instance_service._on_acquire_item = AsyncMock()
        
        # Act
        result = await inventory_service.add_item_to_inventory(inventory_id, item_id, 1, None, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        inventory_service.dao.add_item_to_inventory.assert_called_once()
        inventory_service.dao.get_one.assert_called_once_with(None, item_id)
        inventory_service.item_instance_service._on_acquire_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_remove_item_from_inventory_success(self, inventory_service, sample_item_instance):
        """Тест успешного удаления предмета из инвентаря."""
        # Arrange
        item_instance_id = 1
        
        inventory_service.dao.get_one = AsyncMock(return_value=sample_item_instance)
        inventory_service.dao.delete_one = AsyncMock()
        
        # Мокаем EffectsService
        mock_effects_service = MagicMock()
        mock_effects_service.remove_effects_by_item_instance = AsyncMock()
        inventory_service.effects_service = mock_effects_service
        
        # Act
        result = await inventory_service.remove_item_from_inventory(item_instance_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert "Предмет удален из инвентаря" in result.data
        inventory_service.dao.get_one.assert_called_once_with(None, item_instance_id)
        inventory_service.dao.delete_one.assert_called_once_with(None, item_instance_id)
        mock_effects_service.remove_effects_by_item_instance.assert_called_once_with(item_instance_id, session=None)

    @pytest.mark.asyncio
    async def test_remove_item_from_inventory_not_found(self, inventory_service):
        """Тест удаления несуществующего предмета из инвентаря."""
        # Arrange
        item_instance_id = 999
        
        inventory_service.dao.get_one = AsyncMock(return_value=None)
        
        # Act
        result = await inventory_service.remove_item_from_inventory(item_instance_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        assert "Экземпляр предмета не найден" in result.message
        inventory_service.dao.get_one.assert_called_once_with(None, item_instance_id)
        inventory_service.dao.delete_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_use_item_success(self, inventory_service, sample_item_instance, sample_item):
        """Тест успешного использования предмета."""
        # Arrange
        item_instance_id = 1
        player_id = uuid4()
        
        inventory_service.dao.get_one = AsyncMock(side_effect=[sample_item_instance, sample_item])
        inventory_service.dao.use_item = AsyncMock(return_value=sample_item_instance)
        inventory_service.item_instance_service._use_item_by_title = AsyncMock(
            return_value={"success": True, "message": "Предмет использован"}
        )
        
        # Act
        result = await inventory_service.use_item(item_instance_id, player_id, None, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert "Предмет использован" in result.data["message"]
        inventory_service.dao.get_one.assert_called()
        inventory_service.dao.use_item.assert_called_once_with(None, item_instance_id)
        inventory_service.item_instance_service._use_item_by_title.assert_called_once()

    @pytest.mark.asyncio
    async def test_use_item_not_found(self, inventory_service):
        """Тест использования несуществующего предмета."""
        # Arrange
        item_instance_id = 999
        player_id = uuid4()
        
        inventory_service.dao.get_one = AsyncMock(return_value=None)
        
        # Act
        result = await inventory_service.use_item(item_instance_id, player_id, None, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        assert "Экземпляр предмета не найден" in result.message
        inventory_service.dao.get_one.assert_called_once_with(None, item_instance_id)
        inventory_service.dao.use_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_use_item_item_not_found(self, inventory_service, sample_item_instance):
        """Тест использования предмета с несуществующим шаблоном."""
        # Arrange
        item_instance_id = 1
        player_id = uuid4()
        
        inventory_service.dao.get_one = AsyncMock(side_effect=[sample_item_instance, None])
        inventory_service.dao.use_item = AsyncMock(return_value=sample_item_instance)
        inventory_service.item_instance_service._use_item_by_title = AsyncMock(
            return_value={"success": False, "message": "Предмет не найден"}
        )
        
        # Act
        result = await inventory_service.use_item(item_instance_id, player_id, None, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        assert "Предмет не найден" in result.data["message"]
        inventory_service.dao.get_one.assert_called()
        inventory_service.dao.use_item.assert_called_once_with(None, item_instance_id)

    @pytest.mark.asyncio
    async def test_get_inventory_items_success(self, inventory_service, sample_item_instance):
        """Тест успешного получения предметов инвентаря."""
        # Arrange
        inventory_id = 1
        items = [sample_item_instance]
        
        inventory_service.dao.search_items_in_inventory = AsyncMock(return_value=items)
        
        # Act
        result = await inventory_service.get_inventory_items(inventory_id, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == sample_item_instance.id
        inventory_service.dao.search_items_in_inventory.assert_called_once_with(None, inventory_id, None)

    @pytest.mark.asyncio
    async def test_get_inventory_items_empty(self, inventory_service):
        """Тест получения пустого инвентаря."""
        # Arrange
        inventory_id = 1
        
        inventory_service.dao.search_items_in_inventory = AsyncMock(return_value=[])
        
        # Act
        result = await inventory_service.get_inventory_items(inventory_id, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        inventory_service.dao.search_items_in_inventory.assert_called_once_with(None, inventory_id, None)

    @pytest.mark.asyncio
    async def test_get_inventory_items_with_filter(self, inventory_service, sample_item_instance):
        """Тест получения предметов инвентаря с фильтром."""
        # Arrange
        inventory_id = 1
        item_name = "кубик"
        items = [sample_item_instance]
        
        inventory_service.dao.search_items_in_inventory = AsyncMock(return_value=items)
        
        # Act
        result = await inventory_service.get_inventory_items(inventory_id, item_name, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        inventory_service.dao.search_items_in_inventory.assert_called_once_with(None, inventory_id, item_name)

    @pytest.mark.asyncio
    async def test_get_inventory_with_items_success(self, inventory_service, sample_inventory, sample_item_instance):
        """Тест успешного получения инвентаря с предметами."""
        # Arrange
        inventory_id = 1
        
        inventory_service.get_by_id = AsyncMock(return_value=sample_inventory)
        inventory_service.get_inventory_items = AsyncMock(return_value=[sample_item_instance])
        
        # Act
        result = await inventory_service.get_inventory_with_items(inventory_id, None)
        
        # Assert
        assert isinstance(result, InventoryWithItems)
        assert result.id == sample_inventory.id
        assert len(result.items) == 1
        assert result.items[0].id == sample_item_instance.id
        inventory_service.get_by_id.assert_called_once_with(inventory_id, None)
        inventory_service.get_inventory_items.assert_called_once_with(inventory_id, None, None)

    @pytest.mark.asyncio
    async def test_get_inventory_with_items_not_found(self, inventory_service):
        """Тест получения несуществующего инвентаря с предметами."""
        # Arrange
        inventory_id = 999
        
        inventory_service.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await inventory_service.get_inventory_with_items(inventory_id, None)
        
        # Assert
        assert result is None
        inventory_service.get_by_id.assert_called_once_with(inventory_id, None)
        inventory_service.get_inventory_items.assert_not_called()

    @pytest.mark.asyncio
    async def test_is_inventory_full_true(self, inventory_service):
        """Тест проверки заполненного инвентаря."""
        # Arrange
        inventory_id = 1
        
        inventory_service.dao.is_inventory_full = AsyncMock(return_value=True)
        
        # Act
        result = await inventory_service.is_inventory_full(inventory_id, None)
        
        # Assert
        assert result is True
        inventory_service.dao.is_inventory_full.assert_called_once_with(None, inventory_id)

    @pytest.mark.asyncio
    async def test_is_inventory_full_false(self, inventory_service):
        """Тест проверки незаполненного инвентаря."""
        # Arrange
        inventory_id = 1
        
        inventory_service.dao.is_inventory_full = AsyncMock(return_value=False)
        
        # Act
        result = await inventory_service.is_inventory_full(inventory_id, None)
        
        # Assert
        assert result is False
        inventory_service.dao.is_inventory_full.assert_called_once_with(None, inventory_id)

    @pytest.mark.asyncio
    async def test_replace_item_in_inventory_success(self, inventory_service, sample_item_instance):
        """Тест успешной замены предмета в инвентаре."""
        # Arrange
        inventory_id = 1
        old_item_instance_id = 1
        new_item_id = 2
        new_uses = 5
        new_modifier_turns = 3
        
        inventory_service.dao.replace_item_in_inventory = AsyncMock(return_value=sample_item_instance)
        
        # Act
        result = await inventory_service.replace_item_in_inventory(
            inventory_id, old_item_instance_id, new_item_id, new_uses, new_modifier_turns, None
        )
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert isinstance(result.data, ItemInstanceResponse)
        inventory_service.dao.replace_item_in_inventory.assert_called_once_with(
            None, {
                "inventory_id": inventory_id,
                "old_item_instance_id": old_item_instance_id,
                "new_item_id": new_item_id,
                "new_uses": new_uses,
                "new_modifier_turns": new_modifier_turns
            }
        )

    @pytest.mark.asyncio
    async def test_replace_item_in_inventory_error(self, inventory_service):
        """Тест замены предмета с ошибкой."""
        # Arrange
        inventory_id = 1
        old_item_instance_id = 1
        new_item_id = 2
        new_uses = 5
        
        inventory_service.dao.replace_item_in_inventory = AsyncMock(
            side_effect=ValueError("Item instance not found in this inventory")
        )
        
        # Act
        result = await inventory_service.replace_item_in_inventory(
            inventory_id, old_item_instance_id, new_item_id, new_uses, None, None
        )
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        assert "Item instance not found" in result.message
        inventory_service.dao.replace_item_in_inventory.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_inventory_by_player_id_success(self, inventory_service, sample_inventory):
        """Тест успешного получения инвентаря по ID игрока."""
        # Arrange
        player_id = uuid4()
        
        inventory_service.find_one_by = AsyncMock(return_value=sample_inventory)
        
        # Act
        result = await inventory_service.get_inventory_by_player_id(player_id, None)
        
        # Assert
        assert isinstance(result, InventoryResponse)
        assert result.id == sample_inventory.id
        inventory_service.find_one_by.assert_called_once_with({'player_id': player_id}, None)

    @pytest.mark.asyncio
    async def test_get_inventory_by_player_id_not_found(self, inventory_service):
        """Тест получения несуществующего инвентаря по ID игрока."""
        # Arrange
        player_id = uuid4()
        
        inventory_service.find_one_by = AsyncMock(return_value=None)
        
        # Act
        result = await inventory_service.get_inventory_by_player_id(player_id, None)
        
        # Assert
        assert result is None
        inventory_service.find_one_by.assert_called_once_with({'player_id': player_id}, None)

    @pytest.mark.asyncio
    async def test_create_inventory_success(self, inventory_service, sample_inventory):
        """Тест успешного создания инвентаря."""
        # Arrange
        inventory_data = InventoryCreate(player_id=uuid4())
        
        inventory_service.create = AsyncMock(return_value=sample_inventory)
        
        # Act
        result = await inventory_service.create_inventory(inventory_data, None)
        
        # Assert
        assert isinstance(result, InventoryResponse)
        assert result.id == sample_inventory.id
        inventory_service.create.assert_called_once_with(inventory_data.model_dump(), None)

    @pytest.mark.asyncio
    async def test_delete_inventory_success(self, inventory_service):
        """Тест успешного удаления инвентаря."""
        # Arrange
        inventory_id = 1
        
        inventory_service.delete = AsyncMock(return_value=True)
        
        # Act
        result = await inventory_service.delete_inventory(inventory_id, None)
        
        # Assert
        assert result is True
        inventory_service.delete.assert_called_once_with(inventory_id, None)

    @pytest.mark.asyncio
    async def test_delete_inventory_not_found(self, inventory_service):
        """Тест удаления несуществующего инвентаря."""
        # Arrange
        inventory_id = 999
        
        inventory_service.delete = AsyncMock(return_value=False)
        
        # Act
        result = await inventory_service.delete_inventory(inventory_id, None)
        
        # Assert
        assert result is False
        inventory_service.delete.assert_called_once_with(inventory_id, None)
