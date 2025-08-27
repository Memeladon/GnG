import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.item_instance_service import ItemInstanceService
from src.services.effects_service import EffectsService
from src.services.inventory_service import InventoryService
from src.database.postgres.sql_enums import EffectType, EffectCategory, ItemType
from src.schemas import ServiceResult


class TestItemLogicIntegration:
    """Интеграционные тесты для проверки логики предметов согласно ITEM_LOGIC.md"""

    @pytest.fixture
    def item_instance_service(self):
        """Создание экземпляра ItemInstanceService для тестирования."""
        return ItemInstanceService()

    @pytest.fixture
    def effects_service(self):
        """Создание экземпляра EffectsService для тестирования."""
        return EffectsService()

    @pytest.fixture
    def inventory_service(self):
        """Создание экземпляра InventoryService для тестирования."""
        return InventoryService()

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
    def target_player(self):
        """Тестовые данные целевого игрока."""
        return MagicMock(
            id=uuid4(),
            username="target_player",
            cell_id=5,
            inventory_id=2
        )

    # ==================== ТЕСТЫ ПРЕДМЕТОВ С БЕСКОНЕЧНЫМИ ЭФФЕКТАМИ ====================

    @pytest.mark.asyncio
    async def test_knowledge_sphere_infinite_effect(self, item_instance_service, sample_player):
        """Тест шара всезнания с бесконечным эффектом."""
        # Arrange
        item_instance = MagicMock(
            id=1,
            item_id=1,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        # Act - использование предмета
        result = await item_instance_service._use_knowledge_sphere(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "Предмет использован, эффект будет удален в конце хода" in result["message"]

    @pytest.mark.asyncio
    async def test_colorful_manga_infinite_effect(self, item_instance_service, sample_player):
        """Тест красочной манги с бесконечным эффектом."""
        # Arrange
        item_instance = MagicMock(
            id=2,
            item_id=2,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        # Act - использование предмета
        result = await item_instance_service._use_colorful_manga(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "Предмет использован, эффект будет удален в конце хода" in result["message"]

    # ==================== ТЕСТЫ ПРЕДМЕТОВ С ВРЕМЕННЫМИ ЭФФЕКТАМИ ====================

    @pytest.mark.asyncio
    async def test_ez_glasses_temporary_effect(self, item_instance_service, sample_player):
        """Тест очков EZ с временным эффектом (2 хода легкой сложности)."""
        # Arrange
        item_instance = MagicMock(
            id=3,
            item_id=3,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_ez_glasses(
            item_instance, sample_player, None, None
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

    @pytest.mark.asyncio
    async def test_rambo_bandana_temporary_effect(self, item_instance_service, sample_player):
        """Тест повязки Рэмбо с временным эффектом (2 хода высокой сложности)."""
        # Arrange
        item_instance = MagicMock(
            id=4,
            item_id=4,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_rambo_bandana(
            item_instance, sample_player, None, None
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

    @pytest.mark.asyncio
    async def test_mohsna_totem_temporary_effect(self, item_instance_service, sample_player):
        """Тест тотема мошны с временным эффектом (защита от ловушек на 2 хода)."""
        # Arrange
        item_instance = MagicMock(
            id=5,
            item_id=5,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        
        # Act
        result = await item_instance_service._use_mohsna_totem(
            item_instance, sample_player, None, None
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

    # ==================== ТЕСТЫ ПРЕДМЕТОВ С ЭФФЕКТАМИ НА ДРУГИХ ИГРОКОВ ====================

    @pytest.mark.asyncio
    async def test_rotten_shawarma_target_effect(self, item_instance_service, sample_player, target_player):
        """Тест тухлой шаурмы с эффектом на целевого игрока (-1 к кубикам на 2 хода)."""
        # Arrange
        item_instance = MagicMock(
            id=6,
            item_id=6,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        item_instance_service.effects_service.add_player_effect = AsyncMock()
        item_instance_service.dao.delete_one = AsyncMock()
        
        # Act
        result = await item_instance_service._use_rotten_shawarma(
            item_instance, sample_player, target_player, None
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
        item_instance_service.dao.delete_one.assert_called_once_with(None, item_instance.id)

    @pytest.mark.asyncio
    async def test_rotten_shawarma_no_target(self, item_instance_service, sample_player):
        """Тест тухлой шаурмы без указания целевого игрока."""
        # Arrange
        item_instance = MagicMock(
            id=6,
            item_id=6,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        # Act
        result = await item_instance_service._use_rotten_shawarma(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указан целевой игрок" in result["message"]

    # ==================== ТЕСТЫ ПРЕДМЕТОВ С МОДИФИКАТОРАМИ ====================

    @pytest.mark.asyncio
    async def test_cheat_dice_modifier(self, item_instance_service, sample_player):
        """Тест читерского кубика с модификатором."""
        # Arrange
        item_instance = MagicMock(
            id=7,
            item_id=7,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        new_dice_value = 6
        kwargs = {"new_dice_value": new_dice_value}
        
        item_instance_service.player_service.update_player = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_cheat_dice(
            item_instance, sample_player, None, None, **kwargs
        )
        
        # Assert
        assert result["success"] is True
        assert f"Значение кубика изменено на {new_dice_value}" in result["message"]
        item_instance_service.player_service.update_player.assert_called_once_with(
            sample_player.id, {"dice_modifier": new_dice_value}
        )

    @pytest.mark.asyncio
    async def test_huybik_dice_modifier(self, item_instance_service, sample_player):
        """Тест кубика хуюбика с модификатором."""
        # Arrange
        item_instance = MagicMock(
            id=8,
            item_id=8,
            inventory_id=1,
            uses=1,
            modifier_turns=None
        )
        
        item_instance_service.player_service.update_player = AsyncMock()
        item_instance_service.dao.use_item = AsyncMock()
        
        # Act
        result = await item_instance_service._use_huybik_dice(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is True
        assert "При следующем броске большее значение кубика будет заменено на 1" in result["message"]
        item_instance_service.player_service.update_player.assert_called_once_with(
            sample_player.id, {"dice_modifier": 1, "game_modifier": "huybik_dice"}
        )

    # ==================== ТЕСТЫ ЖИЗНЕННОГО ЦИКЛА ЭФФЕКТОВ ====================

    @pytest.mark.asyncio
    async def test_effect_lifecycle_temporary(self, effects_service):
        """Тест жизненного цикла временного эффекта."""
        # Arrange
        player_id = uuid4()
        effect = MagicMock(
            id=1,
            turns_remaining=2,
            effect_name="test_effect"
        )
        
        effects_service.get_player_effects = AsyncMock(return_value=[effect])
        effects_service.dao.update_one = AsyncMock()
        
        # Act - уменьшение ходов
        result = await effects_service.decrement_effect_turns(player_id, None)
        
        # Assert
        assert result.success is True
        effects_service.dao.update_one.assert_called_once_with(
            None, {
                "id": effect.id,
                "turns_remaining": 1
            }
        )

    @pytest.mark.asyncio
    async def test_effect_lifecycle_expired(self, effects_service):
        """Тест жизненного цикла истекшего эффекта."""
        # Arrange
        player_id = uuid4()
        effect = MagicMock(
            id=1,
            turns_remaining=1,
            effect_name="expired_effect"
        )
        
        effects_service.get_player_effects = AsyncMock(return_value=[effect])
        effects_service.dao.delete_one = AsyncMock()
        
        # Act - уменьшение ходов до 0
        result = await effects_service.decrement_effect_turns(player_id, None)
        
        # Assert
        assert result.success is True
        effects_service.dao.delete_one.assert_called_once_with(None, effect.id)

    @pytest.mark.asyncio
    async def test_effect_lifecycle_infinite(self, effects_service):
        """Тест жизненного цикла бесконечного эффекта."""
        # Arrange
        player_id = uuid4()
        effect = MagicMock(
            id=1,
            turns_remaining=None,  # Бесконечный эффект
            effect_name="infinite_effect"
        )
        
        effects_service.get_player_effects = AsyncMock(return_value=[effect])
        effects_service.dao.update_one = AsyncMock()
        
        # Act - попытка уменьшения ходов
        result = await effects_service.decrement_effect_turns(player_id, None)
        
        # Assert
        assert result.success is True
        # Бесконечные эффекты не должны обновляться
        effects_service.dao.update_one.assert_not_called()

    # ==================== ТЕСТЫ КОНФЛИКТОВ МЕЖДУ ПРЕДМЕТАМИ ====================

    @pytest.mark.asyncio
    async def test_item_conflicts_cheat_huybik(self, effects_service):
        """Тест конфликта между читерским кубиком и кубиком хуюбика."""
        # Arrange
        player_id = uuid4()
        cheat_effect = MagicMock(effect_name="Читерский кубик")
        huybik_effect = MagicMock(effect_name="Кубик хуюбика")
        effects = [cheat_effect, huybik_effect]
        
        effects_service.get_player_effects = AsyncMock(return_value=effects)
        
        # Act
        result = await effects_service.check_effect_conflicts(player_id, None)
        
        # Assert
        assert result.success is True
        assert len(result.data["conflicts"]) > 0
        # Проверяем, что найден конфликт между этими предметами
        conflict_found = any(
            "Читерский кубик" in conflict["effects"] and "Кубик хуюбика" in conflict["effects"]
            for conflict in result.data["conflicts"]
        )
        assert conflict_found

    @pytest.mark.asyncio
    async def test_item_conflicts_ez_rambo(self, effects_service):
        """Тест конфликта между очками EZ и повязкой Рэмбо."""
        # Arrange
        player_id = uuid4()
        ez_effect = MagicMock(effect_name="Очки EZ")
        rambo_effect = MagicMock(effect_name="Повязка Рэмбо")
        effects = [ez_effect, rambo_effect]
        
        effects_service.get_player_effects = AsyncMock(return_value=effects)
        
        # Act
        result = await effects_service.check_effect_conflicts(player_id, None)
        
        # Assert
        assert result.success is True
        assert len(result.data["conflicts"]) > 0
        # Проверяем, что найден конфликт между этими предметами
        conflict_found = any(
            "Очки EZ" in conflict["effects"] and "Повязка Рэмбо" in conflict["effects"]
            for conflict in result.data["conflicts"]
        )
        assert conflict_found

    # ==================== ТЕСТЫ ИНТЕГРАЦИИ С ИНВЕНТАРЕМ ====================

    @pytest.mark.asyncio
    async def test_add_item_with_effect_trigger(self, inventory_service, sample_player):
        """Тест добавления предмета с автоматическим срабатыванием эффекта."""
        # Arrange
        inventory_id = 1
        item_id = 1
        item = MagicMock(
            id=item_id,
            title="Шар всезнания",
            type=ItemType.MODIFIER
        )
        item_instance = MagicMock(
            id=1,
            item_id=item_id,
            inventory_id=inventory_id,
            uses=1
        )
        
        inventory_service.dao.add_item_to_inventory = AsyncMock(return_value=item_instance)
        inventory_service.dao.get_one = AsyncMock(return_value=item)
        inventory_service.item_instance_service._on_acquire_item = AsyncMock()
        
        # Act
        result = await inventory_service.add_item_to_inventory(inventory_id, item_id, 1, None, None)
        
        # Assert
        assert result.success is True
        inventory_service.item_instance_service._on_acquire_item.assert_called_once_with(
            item.title, item_instance, inventory_id, None
        )

    @pytest.mark.asyncio
    async def test_use_item_with_effect_removal(self, inventory_service, sample_player):
        """Тест использования предмета с удалением связанных эффектов."""
        # Arrange
        item_instance_id = 1
        item_instance = MagicMock(
            id=item_instance_id,
            item_id=1,
            inventory_id=1,
            uses=1
        )
        item = MagicMock(
            id=1,
            title="Читерский кубик",
            type=ItemType.MODIFIER
        )
        
        inventory_service.dao.get_one = AsyncMock(side_effect=[item_instance, item])
        inventory_service.dao.use_item = AsyncMock(return_value=item_instance)
        inventory_service.item_instance_service._use_item_by_title = AsyncMock(
            return_value={"success": True, "message": "Предмет использован"}
        )
        
        # Act
        result = await inventory_service.use_item(item_instance_id, sample_player.id, None, None)
        
        # Assert
        assert result.success is True
        assert "Предмет использован" in result.data["message"]
        inventory_service.dao.use_item.assert_called_once_with(None, item_instance_id)

    # ==================== ТЕСТЫ ВАЛИДАЦИИ ВХОДНЫХ ДАННЫХ ====================

    @pytest.mark.asyncio
    async def test_cheat_dice_validation(self, item_instance_service, sample_player):
        """Тест валидации входных данных для читерского кубика."""
        # Arrange
        item_instance = MagicMock(
            id=1,
            item_id=1,
            inventory_id=1,
            uses=1
        )
        
        # Act - без указания нового значения
        result = await item_instance_service._use_cheat_dice(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указано новое значение кубика" in result["message"]

    @pytest.mark.asyncio
    async def test_reroll_scroll_validation(self, item_instance_service, sample_player):
        """Тест валидации входных данных для свитка реролла."""
        # Arrange
        item_instance = MagicMock(
            id=1,
            item_id=1,
            inventory_id=1,
            uses=1
        )
        
        # Act - без указания ID игры
        result = await item_instance_service._use_reroll_scroll(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указан ID игры для реролла" in result["message"]

    @pytest.mark.asyncio
    async def test_explosive_validation(self, item_instance_service, sample_player):
        """Тест валидации входных данных для взрывчатки."""
        # Arrange
        item_instance = MagicMock(
            id=1,
            item_id=1,
            inventory_id=1,
            uses=1
        )
        
        # Act - без указания стороны монетки
        result = await item_instance_service._use_explosive(
            item_instance, sample_player, None, None
        )
        
        # Assert
        assert result["success"] is False
        assert "Не указана сторона монетки" in result["message"]
