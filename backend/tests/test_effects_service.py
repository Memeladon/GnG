import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.effects_service import EffectsService
from src.schemas.player_effects import PlayerEffectsCreate, PlayerEffectsResponse
from src.database.postgres.sql_enums import EffectType, EffectCategory
from src.schemas import ServiceResult


class TestEffectsService:
    """Тесты для EffectsService по паттерну AAA (Arrange, Act, Assert)"""

    @pytest.fixture
    def effects_service(self):
        """Создание экземпляра EffectsService для тестирования."""
        return EffectsService()

    @pytest.fixture
    def sample_effect(self):
        """Тестовые данные эффекта игрока."""
        return MagicMock(
            id=1,
            player_id=uuid4(),
            effect_name="ez_difficulty",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=2,
            is_active=True,
            effect_data={},
            item_instance_id=1
        )

    @pytest.fixture
    def sample_cell(self):
        """Тестовые данные клетки."""
        return MagicMock(
            id=1,
            position=0,
            title="Старт",
            type="start",
            background_image="start.png",
            main_conditions="MAIN",
            genre_conditions="ALL",
            game_conditions="MAIN",
            traps={"test_trap": {"uses_remaining": 3, "data": {"effect": "test"}}}
        )

    # ==================== ТЕСТЫ ЭФФЕКТОВ ИГРОКА ====================

    @pytest.mark.asyncio
    async def test_add_player_effect_success(self, effects_service, sample_effect):
        """Тест успешного добавления эффекта игроку."""
        # Arrange
        player_id = uuid4()
        effect_name = "ez_difficulty"
        effect_type = EffectType.BUFF
        effect_category = EffectCategory.GAME_MODIFIER
        turns_remaining = 2
        effect_data = {"difficulty": "easy"}
        item_instance_id = 1
        
        effects_service.dao.create_one = AsyncMock(return_value=sample_effect)
        
        # Act
        result = await effects_service.add_player_effect(
            player_id, effect_name, effect_type, effect_category, 
            turns_remaining, effect_data, item_instance_id, None
        )
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert isinstance(result.data, PlayerEffectsResponse)
        assert result.data.effect_name == effect_name
        effects_service.dao.create_one.assert_called_once_with(
            None, {
                "player_id": player_id,
                "effect_name": effect_name,
                "effect_type": effect_type,
                "effect_category": effect_category,
                "turns_remaining": turns_remaining,
                "effect_data": effect_data,
                "item_instance_id": item_instance_id
            }
        )

    @pytest.mark.asyncio
    async def test_add_player_effect_without_optional_params(self, effects_service, sample_effect):
        """Тест добавления эффекта игроку без опциональных параметров."""
        # Arrange
        player_id = uuid4()
        effect_name = "test_effect"
        effect_type = EffectType.BUFF
        effect_category = EffectCategory.GAME_MODIFIER
        
        effects_service.dao.create_one = AsyncMock(return_value=sample_effect)
        
        # Act
        result = await effects_service.add_player_effect(
            player_id, effect_name, effect_type, effect_category, session=None
        )
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.dao.create_one.assert_called_once_with(
            None, {
                "player_id": player_id,
                "effect_name": effect_name,
                "effect_type": effect_type,
                "effect_category": effect_category,
                "turns_remaining": 0,
                "effect_data": {},
                "item_instance_id": None
            }
        )

    @pytest.mark.asyncio
    async def test_get_player_effects_success(self, effects_service, sample_effect):
        """Тест успешного получения эффектов игрока."""
        # Arrange
        player_id = uuid4()
        effects = [sample_effect]
        
        effects_service.dao.get_many = AsyncMock(return_value=effects)
        
        # Act
        result = await effects_service.get_player_effects(player_id, None, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].effect_name == sample_effect.effect_name
        effects_service.dao.get_many.assert_called_once_with(
            None, {"player_id": player_id, "is_active": True}
        )

    @pytest.mark.asyncio
    async def test_get_player_effects_with_type_filter(self, effects_service, sample_effect):
        """Тест получения эффектов игрока с фильтром по типу."""
        # Arrange
        player_id = uuid4()
        effect_type = EffectType.BUFF
        effects = [sample_effect]
        
        effects_service.dao.get_many = AsyncMock(return_value=effects)
        
        # Act
        result = await effects_service.get_player_effects(player_id, effect_type, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        effects_service.dao.get_many.assert_called_once_with(
            None, {"player_id": player_id, "is_active": True, "effect_type": effect_type}
        )

    @pytest.mark.asyncio
    async def test_get_player_effects_empty(self, effects_service):
        """Тест получения пустого списка эффектов игрока."""
        # Arrange
        player_id = uuid4()
        
        effects_service.dao.get_many = AsyncMock(return_value=[])
        
        # Act
        result = await effects_service.get_player_effects(player_id, None, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        effects_service.dao.get_many.assert_called_once_with(
            None, {"player_id": player_id, "is_active": True}
        )

    @pytest.mark.asyncio
    async def test_decrement_effect_turns_success(self, effects_service, sample_effect):
        """Тест успешного уменьшения ходов эффектов."""
        # Arrange
        player_id = uuid4()
        effects = [sample_effect]
        
        effects_service.get_player_effects = AsyncMock(return_value=effects)
        effects_service.dao.update_one = AsyncMock()
        effects_service.dao.delete_one = AsyncMock()
        
        # Act
        result = await effects_service.decrement_effect_turns(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.get_player_effects.assert_called_once_with(player_id, None, session=None)
        effects_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_decrement_effect_turns_expired_effect(self, effects_service):
        """Тест уменьшения ходов с истекшим эффектом."""
        # Arrange
        player_id = uuid4()
        expired_effect = MagicMock(
            id=1,
            turns_remaining=1,
            effect_name="expired_effect"
        )
        effects = [expired_effect]
        
        effects_service.get_player_effects = AsyncMock(return_value=effects)
        effects_service.dao.delete_one = AsyncMock()
        
        # Act
        result = await effects_service.decrement_effect_turns(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.dao.delete_one.assert_called_once_with(None, expired_effect.id)

    @pytest.mark.asyncio
    async def test_remove_player_effect_success(self, effects_service, sample_effect):
        """Тест успешного удаления эффекта игрока."""
        # Arrange
        player_id = uuid4()
        effect_name = "ez_difficulty"
        
        effects_service.dao.get_many = AsyncMock(return_value=[sample_effect])
        effects_service.dao.delete_one = AsyncMock()
        
        # Act
        result = await effects_service.remove_player_effect(player_id, effect_name, None)
        
        # Assert
        assert result is True
        effects_service.dao.get_many.assert_called_once_with(
            None, {"player_id": player_id, "effect_name": effect_name, "is_active": True}
        )
        effects_service.dao.delete_one.assert_called_once_with(None, sample_effect.id)

    @pytest.mark.asyncio
    async def test_remove_player_effect_not_found(self, effects_service):
        """Тест удаления несуществующего эффекта игрока."""
        # Arrange
        player_id = uuid4()
        effect_name = "nonexistent_effect"
        
        effects_service.dao.get_many = AsyncMock(return_value=[])
        
        # Act
        result = await effects_service.remove_player_effect(player_id, effect_name, None)
        
        # Assert
        assert result is False
        effects_service.dao.get_many.assert_called_once_with(
            None, {"player_id": player_id, "effect_name": effect_name, "is_active": True}
        )

    @pytest.mark.asyncio
    async def test_on_game_completed_success(self, effects_service, sample_effect):
        """Тест успешного завершения игры с эффектами."""
        # Arrange
        player_id = uuid4()
        effects = [sample_effect]
        
        effects_service.dao.get_many = AsyncMock(return_value=effects)
        effects_service.dao.get_one = AsyncMock(return_value=None)  # ItemInstance не существует
        effects_service.dao.delete_one = AsyncMock()
        effects_service.decrement_effect_turns = AsyncMock(return_value=ServiceResult(success=True))
        
        # Act
        result = await effects_service.on_game_completed(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.dao.get_many.assert_called()
        effects_service.dao.delete_one.assert_called_once_with(None, sample_effect.id)
        effects_service.decrement_effect_turns.assert_called_once_with(player_id, session=None)

    @pytest.mark.asyncio
    async def test_remove_effects_by_item_instance_success(self, effects_service, sample_effect):
        """Тест успешного удаления эффектов по экземпляру предмета."""
        # Arrange
        item_instance_id = 1
        effects = [sample_effect]
        
        effects_service.dao.get_many = AsyncMock(return_value=effects)
        effects_service.dao.delete_one = AsyncMock()
        
        # Act
        result = await effects_service.remove_effects_by_item_instance(item_instance_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert result.data["count"] == 1
        assert sample_effect.effect_name in result.data["removed_effects"]
        effects_service.dao.get_many.assert_called_once_with(
            None, {"item_instance_id": item_instance_id, "is_active": True}
        )
        effects_service.dao.delete_one.assert_called_once_with(None, sample_effect.id)

    @pytest.mark.asyncio
    async def test_remove_effects_by_item_instance_empty(self, effects_service):
        """Тест удаления эффектов по несуществующему экземпляру предмета."""
        # Arrange
        item_instance_id = 999
        
        effects_service.dao.get_many = AsyncMock(return_value=[])
        
        # Act
        result = await effects_service.remove_effects_by_item_instance(item_instance_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert result.data["count"] == 0
        assert len(result.data["removed_effects"]) == 0
        effects_service.dao.get_many.assert_called_once_with(
            None, {"item_instance_id": item_instance_id, "is_active": True}
        )

    # ==================== ТЕСТЫ ЛОВУШЕК НА КЛЕТКАХ ====================

    @pytest.mark.asyncio
    async def test_add_trap_to_cell_success(self, effects_service, sample_cell):
        """Тест успешного добавления ловушки на клетку."""
        # Arrange
        cell_id = 1
        trap_data = {"name": "test_trap", "effect": "test"}
        
        effects_service.dao.add_trap_to_cell = AsyncMock(return_value=sample_cell)
        
        # Act
        result = await effects_service.add_trap_to_cell(cell_id, trap_data, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.dao.add_trap_to_cell.assert_called_once_with(None, cell_id, trap_data)

    @pytest.mark.asyncio
    async def test_remove_trap_from_cell_success(self, effects_service, sample_cell):
        """Тест успешного удаления ловушки с клетки."""
        # Arrange
        cell_id = 1
        trap_index = 0
        
        effects_service.dao.remove_trap_from_cell = AsyncMock(return_value=sample_cell)
        
        # Act
        result = await effects_service.remove_trap_from_cell(cell_id, trap_index, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.dao.remove_trap_from_cell.assert_called_once_with(None, cell_id, trap_index)

    @pytest.mark.asyncio
    async def test_get_cell_traps_success(self, effects_service, sample_cell):
        """Тест успешного получения ловушек клетки."""
        # Arrange
        cell_id = 1
        
        effects_service.dao.get_cell_traps = AsyncMock(return_value=sample_cell.traps)
        
        # Act
        result = await effects_service.get_cell_traps(cell_id, None)
        
        # Assert
        assert isinstance(result, dict)
        assert "test_trap" in result
        effects_service.dao.get_cell_traps.assert_called_once_with(None, cell_id)

    @pytest.mark.asyncio
    async def test_get_cell_traps_empty(self, effects_service):
        """Тест получения ловушек пустой клетки."""
        # Arrange
        cell_id = 1
        
        effects_service.dao.get_cell_traps = AsyncMock(return_value={})
        
        # Act
        result = await effects_service.get_cell_traps(cell_id, None)
        
        # Assert
        assert isinstance(result, dict)
        assert len(result) == 0
        effects_service.dao.get_cell_traps.assert_called_once_with(None, cell_id)

    @pytest.mark.asyncio
    async def test_use_cell_trap_success(self, effects_service, sample_cell):
        """Тест успешного использования ловушки на клетке."""
        # Arrange
        cell_id = 1
        trap_name = "test_trap"
        
        effects_service.dao.get_one = AsyncMock(return_value=sample_cell)
        effects_service.dao.update_one = AsyncMock()
        
        # Act
        result = await effects_service.use_cell_trap(cell_id, trap_name, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert result.data["trap_name"] == trap_name
        assert result.data["uses_remaining"] == 2  # Уменьшилось с 3 до 2
        effects_service.dao.get_one.assert_called_once_with(None, cell_id)
        effects_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_use_cell_trap_not_found(self, effects_service):
        """Тест использования несуществующей ловушки."""
        # Arrange
        cell_id = 1
        trap_name = "nonexistent_trap"
        
        effects_service.dao.get_one = AsyncMock(return_value=None)
        
        # Act
        result = await effects_service.use_cell_trap(cell_id, trap_name, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        assert "Ловушка не найдена" in result.message
        effects_service.dao.get_one.assert_called_once_with(None, cell_id)

    @pytest.mark.asyncio
    async def test_use_cell_trap_last_use(self, effects_service):
        """Тест использования ловушки с последним зарядом."""
        # Arrange
        cell_id = 1
        trap_name = "test_trap"
        cell_with_last_use = MagicMock(
            id=1,
            traps={trap_name: {"uses_remaining": 1, "data": {"effect": "test"}}}
        )
        
        effects_service.dao.get_one = AsyncMock(return_value=cell_with_last_use)
        effects_service.dao.update_one = AsyncMock()
        
        # Act
        result = await effects_service.use_cell_trap(cell_id, trap_name, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert result.data["uses_remaining"] == 0
        effects_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_cell_trap_success(self, effects_service, sample_cell):
        """Тест успешного удаления ловушки с клетки."""
        # Arrange
        cell_id = 1
        trap_name = "test_trap"
        
        effects_service.dao.get_one = AsyncMock(return_value=sample_cell)
        effects_service.dao.update_one = AsyncMock()
        
        # Act
        result = await effects_service.remove_cell_trap(cell_id, trap_name, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        effects_service.dao.get_one.assert_called_once_with(None, cell_id)
        effects_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_cell_trap_not_found(self, effects_service):
        """Тест удаления несуществующей ловушки."""
        # Arrange
        cell_id = 1
        trap_name = "nonexistent_trap"
        
        effects_service.dao.get_one = AsyncMock(return_value=None)
        
        # Act
        result = await effects_service.remove_cell_trap(cell_id, trap_name, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is False
        effects_service.dao.get_one.assert_called_once_with(None, cell_id)

    # ==================== ТЕСТЫ ВСПОМОГАТЕЛЬНЫХ МЕТОДОВ ====================

    @pytest.mark.asyncio
    async def test_check_effect_conflicts_success(self, effects_service, sample_effect):
        """Тест успешной проверки конфликтов эффектов."""
        # Arrange
        player_id = uuid4()
        effects = [sample_effect]
        
        effects_service.get_player_effects = AsyncMock(return_value=effects)
        
        # Act
        result = await effects_service.check_effect_conflicts(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert "conflicts" in result.data
        assert "total_effects" in result.data
        assert result.data["total_effects"] == 1
        effects_service.get_player_effects.assert_called_once_with(player_id, None, session=None)

    @pytest.mark.asyncio
    async def test_check_effect_conflicts_with_conflicts(self, effects_service):
        """Тест проверки конфликтов эффектов с обнаруженными конфликтами."""
        # Arrange
        player_id = uuid4()
        cheat_effect = MagicMock(effect_name="Читерский кубик")
        huybik_effect = MagicMock(effect_name="Кубик хуюбика")
        effects = [cheat_effect, huybik_effect]
        
        effects_service.get_player_effects = AsyncMock(return_value=effects)
        
        # Act
        result = await effects_service.check_effect_conflicts(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert len(result.data["conflicts"]) > 0
        effects_service.get_player_effects.assert_called_once_with(player_id, None, session=None)

    @pytest.mark.asyncio
    async def test_resolve_effect_conflicts_success(self, effects_service):
        """Тест успешного разрешения конфликтов эффектов."""
        # Arrange
        player_id = uuid4()
        conflicts_data = {
            "conflicts": [
                {
                    "type": "destruction",
                    "effects": ["Читерский кубик", "Кубик хуюбика"]
                }
            ]
        }
        
        effects_service.check_effect_conflicts = AsyncMock(return_value=ServiceResult(success=True, data=conflicts_data))
        effects_service.remove_player_effect = AsyncMock(return_value=True)
        
        # Act
        result = await effects_service.resolve_effect_conflicts(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert "resolved_conflicts" in result.data
        effects_service.check_effect_conflicts.assert_called_once_with(player_id, session=None)
        assert effects_service.remove_player_effect.call_count == 2

    @pytest.mark.asyncio
    async def test_resolve_effect_conflicts_no_conflicts(self, effects_service):
        """Тест разрешения конфликтов эффектов без конфликтов."""
        # Arrange
        player_id = uuid4()
        conflicts_data = {"conflicts": []}
        
        effects_service.check_effect_conflicts = AsyncMock(return_value=ServiceResult(success=True, data=conflicts_data))
        
        # Act
        result = await effects_service.resolve_effect_conflicts(player_id, None)
        
        # Assert
        assert isinstance(result, ServiceResult)
        assert result.success is True
        assert len(result.data["resolved_conflicts"]) == 0
        effects_service.check_effect_conflicts.assert_called_once_with(player_id, session=None)
