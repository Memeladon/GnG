import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.item_instance_service import ItemInstanceService
from src.schemas.item_instance import ItemInstanceCreate, ItemInstanceResponse
from src.database.postgres.sql_enums import ItemType, EffectType, EffectCategory
from src.schemas import ServiceResult


class TestItemInstanceService:
    """Тесты для ItemInstanceService по паттерну AAA (Arrange, Act, Assert)"""

    @pytest.fixture
    def item_instance_service(self):
        """Создание экземпляра ItemInstanceService для тестирования."""
        return ItemInstanceService()

    @pytest.fixture
    def sample_player(self):
        """Тестовые данные игрока."""
        return MagicMock(
            id=uuid4(),
            username="test_player",
            cell_id=0,
            inventory_id=1
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

    @pytest.fixture
    def sample_item(self):
        """Тестовые данные предмета."""
        return MagicMock(
            id=1,
            title="Читерский кубик",
            description="Позволяет заменить значение кубика",
            type=ItemType.MODIFIER
        )

    @pytest.fixture
    def target_player(self):
        """Тестовые данные целевого игрока."""
        return MagicMock(
            id=uuid4(),
            username="target_player",
            cell_id=5,
            inventory_id=2
        )

    # ==================== ТЕСТЫ ЛОГИКИ ПРЕДМЕТОВ ====================

    @pytest.mark.asyncio
    async def test_use_cheat_dice_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования читерского кубика."""
        # Arrange
        new_dice_value = 6
        kwargs = {"new_dice_value": new_dice_value}
        
        item_instance_service.player_service.update_player = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_cheat_dice(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert f"Значение кубика изменено на {new_dice_value}" in result["message"]
        item_instance_service.player_service.update_player.assert_called_once_with(
            sample_player.id, {"dice_modifier": new_dice_value}
        )
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_cheat_dice_no_value(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования читерского кубика без указания значения."""
        # Arrange
        kwargs = {}
        
        # Act
        result = await item_instance_service._use_cheat_dice(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указано новое значение кубика" in result["message"]

    @pytest.mark.asyncio
    async def test_use_huybik_dice_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования кубика хуюбика."""
        # Arrange
        item_instance_service.player_service.update_player = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_huybik_dice(
            sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "При следующем броске большее значение кубика будет заменено на 1" in result["message"]
        item_instance_service.player_service.update_player.assert_called_once_with(
            sample_player.id, {"dice_modifier": 1, "game_modifier": "huybik_dice"}
        )
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_ez_glasses_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования очков EZ."""
        # Arrange
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_ez_glasses(
            sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "Следующие 2 хода игры будут на легком уровне сложности" in result["message"]
        item_instance_service.effects_service.add_player_effect.assert_called_once_with(
            player_id=sample_player.id,
            effect_name="ez_difficulty",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=2,
            session=None
        )
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_rambo_bandana_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования повязки Рэмбо."""
        # Arrange
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_rambo_bandana(
            sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "Следующие 2 хода игры будут на высоком уровне сложности" in result["message"]
        item_instance_service.effects_service.add_player_effect.assert_called_once_with(
            player_id=sample_player.id,
            effect_name="rambo_difficulty",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=2,
            session=None
        )
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_reroll_scroll_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования свитка реролла."""
        # Arrange
        game_id = 123
        kwargs = {"game_id": game_id}
        game_data = {"id": game_id, "status": "rerolled"}
        
        item_instance_service.game_service.reroll_game = AsyncMock(return_value=game_data)
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_reroll_scroll(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert "Игра перезапущена" in result["message"]
        assert result["game_data"] == game_data
        item_instance_service.game_service.reroll_game.assert_called_once_with(game_id)
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_reroll_scroll_no_game_id(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования свитка реролла без указания ID игры."""
        # Arrange
        kwargs = {}
        
        # Act
        result = await item_instance_service._use_reroll_scroll(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указан ID игры для реролла" in result["message"]

    @pytest.mark.asyncio
    async def test_use_knowledge_sphere_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования шара всезнания."""
        # Arrange
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_knowledge_sphere(
            sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "Предмет использован, эффект будет удален в конце хода" in result["message"]
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_explosive_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования взрывчатки."""
        # Arrange
        coin_side = "heads"
        kwargs = {"coin_side": coin_side}
        
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_explosive(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert "Взрывчатка использована" in result["message"]
        item_instance_service.dao.use_item.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_explosive_no_coin_side(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования взрывчатки без указания стороны монетки."""
        # Arrange
        kwargs = {}
        
        # Act
        result = await item_instance_service._use_explosive(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указана сторона монетки" in result["message"]

    @pytest.mark.asyncio
    async def test_use_rotten_shawarma_success(self, item_instance_service, sample_item_instance, sample_player, target_player):
        """Тест успешного использования тухлой шаурмы."""
        # Arrange
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        item_instance_service.dao.delete_one = AsyncMock()
        
        # Act
        result = await item_instance_service._use_rotten_shawarma(
            sample_item_instance, sample_player, target_player, None
        )
        
        # Assert
        assert result["success"] is True
        assert f"Игрок {target_player.username} получил -1 к кубикам на 2 хода" in result["message"]
        item_instance_service.effects_service.add_player_effect.assert_called_once_with(
            player_id=target_player.id,
            effect_name="rotten_shawarma",
            effect_type=EffectType.DEBUFF,
            effect_category=EffectCategory.MOVEMENT,
            turns_remaining=2,
            effect_data={"dice_penalty": 1},
            session=None
        )
        item_instance_service.dao.delete_one.assert_called_once_with(None, sample_item_instance.id)

    @pytest.mark.asyncio
    async def test_use_rotten_shawarma_no_target(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования тухлой шаурмы без целевого игрока."""
        # Arrange
        
        # Act
        result = await item_instance_service._use_rotten_shawarma(
            sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указан целевой игрок" in result["message"]

    @pytest.mark.asyncio
    async def test_use_mohsna_totem_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования тотема мошны."""
        # Arrange
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        
        # Act
        result = await item_instance_service._use_mohsna_totem(
            sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "Защита от ловушек-событий активирована на 2 хода" in result["message"]
        item_instance_service.effects_service.add_player_effect.assert_called_once_with(
            player_id=sample_player.id,
            effect_name="trap_protection",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.PROTECTION,
            turns_remaining=2,
            session=None
        )

    @pytest.mark.asyncio
    async def test_use_plus_notebook_doubles_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного использования плюсового блокнота с одинаковыми значениями."""
        # Arrange
        dice_values = [6, 6]
        kwargs = {"dice_values": dice_values}
        
        # Act
        result = await item_instance_service._use_plus_notebook(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert "Выпали две шестерки! Получено +1 очко" in result["message"]
        assert result["bonus_points"] == 1

    @pytest.mark.asyncio
    async def test_use_plus_notebook_other_doubles(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования плюсового блокнота с другими одинаковыми значениями."""
        # Arrange
        dice_values = [3, 3]
        kwargs = {"dice_values": dice_values}
        
        # Act
        result = await item_instance_service._use_plus_notebook(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert "Выпали одинаковые значения! +2 к движению" in result["message"]
        assert result["movement_bonus"] == 2

    @pytest.mark.asyncio
    async def test_use_plus_notebook_normal_roll(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования плюсового блокнота с обычным броском."""
        # Arrange
        dice_values = [2, 5]
        kwargs = {"dice_values": dice_values}
        
        # Act
        result = await item_instance_service._use_plus_notebook(
            sample_item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert "Обычный бросок кубиков" in result["message"]

    # ==================== ТЕСТЫ ВСПОМОГАТЕЛЬНЫХ МЕТОДОВ ====================

    @pytest.mark.asyncio
    async def test_use_item_by_title_success(self, item_instance_service, sample_item_instance, sample_player):
        """Тест успешного делегирования использования по названию предмета."""
        # Arrange
        title = "Читерский кубик"
        expected_result = {"success": True, "message": "Предмет использован"}
        
        item_instance_service._use_cheat_dice = AsyncMock(return_value=expected_result)
        
        # Act
        result = await item_instance_service._use_item_by_title(
            title, sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result == expected_result
        item_instance_service._use_cheat_dice.assert_called_once_with(
            sample_item_instance, sample_player, None, None
        )

    @pytest.mark.asyncio
    async def test_use_item_by_title_handler_not_found(self, item_instance_service, sample_item_instance, sample_player):
        """Тест использования предмета с несуществующим обработчиком."""
        # Arrange
        title = "Несуществующий предмет"
        
        # Act
        result = await item_instance_service._use_item_by_title(
            title, sample_item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is False
        assert f"Обработчик для предмета '{title}' не найден" in result["message"]

    @pytest.mark.asyncio
    async def test_check_effect_conflicts_success(self, item_instance_service, sample_player):
        """Тест успешной проверки конфликтов эффектов."""
        # Arrange
        expected_result = {"conflicts": [], "total_effects": 0}
        item_instance_service.effects_service.check_effect_conflicts = AsyncMock(return_value=expected_result)
        
        # Act
        result = await item_instance_service._check_effect_conflicts(sample_player, None)
        
        # Assert
        assert result == expected_result
        item_instance_service.effects_service.check_effect_conflicts.assert_called_once_with(sample_player.id, session=None)

    @pytest.mark.asyncio
    async def test_resolve_effect_conflicts_success(self, item_instance_service, sample_player):
        """Тест успешного разрешения конфликтов эффектов."""
        # Arrange
        expected_result = {"resolved_conflicts": []}
        item_instance_service.effects_service.resolve_effect_conflicts = AsyncMock(return_value=expected_result)
        
        # Act
        result = await item_instance_service._resolve_effect_conflicts(sample_player, None)
        
        # Assert
        assert result == expected_result
        item_instance_service.effects_service.resolve_effect_conflicts.assert_called_once_with(sample_player.id, session=None)

    # ==================== ТЕСТЫ ОСНОВНЫХ МЕТОДОВ ====================

    @pytest.mark.asyncio
    async def test_create_item_instance_success(self, item_instance_service, sample_item_instance):
        """Тест успешного создания экземпляра предмета."""
        # Arrange
        item_instance_data = ItemInstanceCreate(
            item_id=1,
            inventory_id=1,
            uses=3
        )
        
        item_instance_service.create = AsyncMock(return_value=sample_item_instance)
        
        # Act
        result = await item_instance_service.create_item_instance(item_instance_data, None)
        
        # Assert
        assert isinstance(result, ItemInstanceResponse)
        assert result.id == sample_item_instance.id
        item_instance_service.create.assert_called_once_with(item_instance_data.model_dump(), None)

    @pytest.mark.asyncio
    async def test_get_item_instance_success(self, item_instance_service, sample_item_instance):
        """Тест успешного получения экземпляра предмета."""
        # Arrange
        item_instance_id = 1
        
        item_instance_service.get_by_id = AsyncMock(return_value=sample_item_instance)
        
        # Act
        result = await item_instance_service.get_item_instance(item_instance_id, None)
        
        # Assert
        assert isinstance(result, ItemInstanceResponse)
        assert result.id == sample_item_instance.id
        item_instance_service.get_by_id.assert_called_once_with(item_instance_id, None)

    @pytest.mark.asyncio
    async def test_get_item_instance_not_found(self, item_instance_service):
        """Тест получения несуществующего экземпляра предмета."""
        # Arrange
        item_instance_id = 999
        
        item_instance_service.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await item_instance_service.get_item_instance(item_instance_id, None)
        
        # Assert
        assert result is None
        item_instance_service.get_by_id.assert_called_once_with(item_instance_id, None)

    @pytest.mark.asyncio
    async def test_update_item_instance_success(self, item_instance_service, sample_item_instance):
        """Тест успешного обновления экземпляра предмета."""
        # Arrange
        item_instance_id = 1
        update_data = {"uses": 2}
        
        item_instance_service.update = AsyncMock(return_value=sample_item_instance)
        
        # Act
        result = await item_instance_service.update_item_instance(item_instance_id, update_data, None)
        
        # Assert
        assert isinstance(result, ItemInstanceResponse)
        assert result.id == sample_item_instance.id
        item_instance_service.update.assert_called_once_with(update_data, None)

    @pytest.mark.asyncio
    async def test_delete_item_instance_success(self, item_instance_service):
        """Тест успешного удаления экземпляра предмета."""
        # Arrange
        item_instance_id = 1
        
        item_instance_service.delete = AsyncMock(return_value=True)
        
        # Act
        result = await item_instance_service.delete_item_instance(item_instance_id, None)
        
        # Assert
        assert result is True
        item_instance_service.delete.assert_called_once_with(item_instance_id, None)

    @pytest.mark.asyncio
    async def test_get_item_instances_by_inventory_success(self, item_instance_service, sample_item_instance):
        """Тест успешного получения экземпляров предметов по инвентарю."""
        # Arrange
        inventory_id = 1
        item_instances = [sample_item_instance]
        
        item_instance_service.find_by = AsyncMock(return_value=item_instances)
        
        # Act
        result = await item_instance_service.get_item_instances_by_inventory(inventory_id, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == sample_item_instance.id
        item_instance_service.find_by.assert_called_once_with({'inventory_id': inventory_id}, None)

    @pytest.mark.asyncio
    async def test_get_item_instances_by_inventory_empty(self, item_instance_service):
        """Тест получения пустого списка экземпляров предметов по инвентарю."""
        # Arrange
        inventory_id = 1
        
        item_instance_service.find_by = AsyncMock(return_value=[])
        
        # Act
        result = await item_instance_service.get_item_instances_by_inventory(inventory_id, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        item_instance_service.find_by.assert_called_once_with({'inventory_id': inventory_id}, None)
