import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.player_service import PlayerService
from src.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerWithRelations
from src.database.postgres.sql_enums import UserRights


class TestPlayerService:
    """Тесты для PlayerService по паттерну AAA (Arrange, Act, Assert)"""

    @pytest.fixture
    def player_service(self):
        """Создание экземпляра PlayerService для тестирования."""
        return PlayerService()

    @pytest.fixture
    def sample_player(self):
        """Тестовые данные игрока."""
        return MagicMock(
            id=uuid4(),
            user_id=uuid4(),
            username="test_player",
            profile_image="test_avatar.png",
            cell_id=0,
            role=UserRights.PLAYER,
            dice_modifier=0,
            game_modifier=0,
            last_dice_value=0,
            previous_cell_id=0,
            inventory_id=1
        )

    @pytest.fixture
    def player_create_data(self):
        """Тестовые данные для создания игрока."""
        return PlayerCreate(
            user_id=uuid4(),
            username="new_player",
            profile_image="new_avatar.png",
            role=UserRights.PLAYER,
            cell_id=0,
            inventory_id=1
        )

    @pytest.mark.asyncio
    async def test_create_player_profile_success(self, player_service, player_create_data, sample_player):
        """Тест успешного создания профиля игрока."""
        # Arrange
        player_service.exists_by = AsyncMock(return_value=False)  # Пользователь не имеет профиля
        player_service.dao.create_player_first_time = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.create_player_profile(player_create_data, None)
        
        # Assert
        assert isinstance(result, PlayerWithRelations)
        assert result.username == sample_player.username
        assert result.user_id == sample_player.user_id
        player_service.exists_by.assert_called_once_with({'user_id': player_create_data.user_id}, None)
        player_service.dao.create_player_first_time.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_player_profile_already_exists(self, player_service, player_create_data):
        """Тест создания профиля игрока, который уже существует."""
        # Arrange
        player_service.exists_by = AsyncMock(return_value=True)  # Пользователь уже имеет профиль
        
        # Act & Assert
        with pytest.raises(ValueError, match="Пользователь уже имеет профиль игрока"):
            await player_service.create_player_profile(player_create_data, None)
        
        player_service.exists_by.assert_called_once_with({'user_id': player_create_data.user_id}, None)
        player_service.dao.create_player_first_time.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_player_profile_username_exists(self, player_service, player_create_data):
        """Тест создания профиля игрока с уже существующим именем пользователя."""
        # Arrange
        player_service.exists_by = AsyncMock(side_effect=[False, True])  # Нет профиля, но есть имя
        
        # Act & Assert
        with pytest.raises(ValueError, match="Игрок с именем 'new_player' уже существует"):
            await player_service.create_player_profile(player_create_data, None)
        
        assert player_service.exists_by.call_count == 2
        player_service.dao.create_player_first_time.assert_not_called()

    @pytest.mark.asyncio
    async def test_roll_dice_success(self, player_service, sample_player):
        """Тест успешного броска кубика."""
        # Arrange
        player_id = uuid4()
        modifiers = {"dice_modifier": 1, "game_modifier": 2}
        player_service.get_by_id = AsyncMock(return_value=sample_player)
        player_service.update = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.roll_dice(player_id, modifiers, None)
        
        # Assert
        assert isinstance(result, dict)
        assert "dice_value" in result
        assert "dice_modifier" in result
        assert "game_modifier" in result
        assert "final_value" in result
        assert 1 <= result["dice_value"] <= 6
        assert result["dice_modifier"] == 1
        assert result["game_modifier"] == 2
        assert 1 <= result["final_value"] <= 6
        player_service.get_by_id.assert_called_once_with(player_id, None)
        player_service.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_roll_dice_player_not_found(self, player_service):
        """Тест броска кубика несуществующим игроком."""
        # Arrange
        player_id = uuid4()
        player_service.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Игрок не найден"):
            await player_service.roll_dice(player_id, {}, None)
        
        player_service.get_by_id.assert_called_once_with(player_id, None)
        player_service.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_roll_dice_no_modifiers(self, player_service, sample_player):
        """Тест броска кубика без модификаторов."""
        # Arrange
        player_id = uuid4()
        player_service.get_by_id = AsyncMock(return_value=sample_player)
        player_service.update = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.roll_dice(player_id, None, None)
        
        # Assert
        assert isinstance(result, dict)
        assert result["dice_modifier"] == 0
        assert result["game_modifier"] == 0
        assert 1 <= result["final_value"] <= 6
        player_service.get_by_id.assert_called_once_with(player_id, None)
        player_service.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_player_success(self, player_service, sample_player):
        """Тест успешного перемещения игрока."""
        # Arrange
        player_id = uuid4()
        steps = 5
        player_service.get_by_id = AsyncMock(return_value=sample_player)
        player_service.update = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.move_player(player_id, steps, None)
        
        # Assert
        assert isinstance(result, PlayerResponse)
        assert result.cell_id == sample_player.cell_id
        player_service.get_by_id.assert_called_once_with(player_id, None)
        player_service.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_player_not_found(self, player_service):
        """Тест перемещения несуществующего игрока."""
        # Arrange
        player_id = uuid4()
        player_service.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Игрок не найден"):
            await player_service.move_player(player_id, 5, None)
        
        player_service.get_by_id.assert_called_once_with(player_id, None)
        player_service.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_player_profile_success(self, player_service, sample_player):
        """Тест успешного обновления профиля игрока."""
        # Arrange
        player_id = uuid4()
        update_data = PlayerUpdate(username="new_username", profile_image="new_avatar.png")
        updated_player = MagicMock(
            id=player_id,
            username="new_username",
            profile_image="new_avatar.png"
        )
        player_service.dao.update_player_profile = AsyncMock(return_value=updated_player)
        
        # Act
        result = await player_service.update_player_profile(player_id, update_data, None)
        
        # Assert
        assert isinstance(result, PlayerResponse)
        assert result.username == "new_username"
        assert result.profile_image == "new_avatar.png"
        player_service.dao.update_player_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_player_profile_not_found(self, player_service):
        """Тест обновления профиля несуществующего игрока."""
        # Arrange
        player_id = uuid4()
        update_data = PlayerUpdate(username="new_username")
        player_service.dao.update_player_profile = AsyncMock(return_value=None)
        
        # Act
        result = await player_service.update_player_profile(player_id, update_data, None)
        
        # Assert
        assert result is None
        player_service.dao.update_player_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_player_by_user_id_success(self, player_service, sample_player):
        """Тест получения игрока по ID пользователя."""
        # Arrange
        user_id = uuid4()
        player_service.find_one_by = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.get_player_by_user_id(user_id, None)
        
        # Assert
        assert isinstance(result, PlayerResponse)
        assert result.user_id == sample_player.user_id
        player_service.find_one_by.assert_called_once_with({'user_id': user_id}, None)

    @pytest.mark.asyncio
    async def test_get_player_by_user_id_not_found(self, player_service):
        """Тест получения несуществующего игрока по ID пользователя."""
        # Arrange
        user_id = uuid4()
        player_service.find_one_by = AsyncMock(return_value=None)
        
        # Act
        result = await player_service.get_player_by_user_id(user_id, None)
        
        # Assert
        assert result is None
        player_service.find_one_by.assert_called_once_with({'user_id': user_id}, None)

    @pytest.mark.asyncio
    async def test_get_player_by_username_success(self, player_service, sample_player):
        """Тест получения игрока по имени пользователя."""
        # Arrange
        username = "test_player"
        player_service.find_one_by = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.get_player_by_username(username, None)
        
        # Assert
        assert isinstance(result, PlayerResponse)
        assert result.username == sample_player.username
        player_service.find_one_by.assert_called_once_with({'username': username}, None)

    @pytest.mark.asyncio
    async def test_get_player_by_username_not_found(self, player_service):
        """Тест получения несуществующего игрока по имени пользователя."""
        # Arrange
        username = "nonexistent"
        player_service.find_one_by = AsyncMock(return_value=None)
        
        # Act
        result = await player_service.get_player_by_username(username, None)
        
        # Assert
        assert result is None
        player_service.find_one_by.assert_called_once_with({'username': username}, None)

    @pytest.mark.asyncio
    async def test_get_players_by_session_id_success(self, player_service, sample_player):
        """Тест получения игроков по ID сессии."""
        # Arrange
        session_id = uuid4()
        players = [sample_player]
        player_service.dao.get_players_by_session_id = AsyncMock(return_value=players)
        
        # Act
        result = await player_service.get_players_by_session_id(session_id, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].username == sample_player.username
        player_service.dao.get_players_by_session_id.assert_called_once_with(None, session_id)

    @pytest.mark.asyncio
    async def test_get_players_by_session_id_empty(self, player_service):
        """Тест получения пустого списка игроков по ID сессии."""
        # Arrange
        session_id = uuid4()
        player_service.dao.get_players_by_session_id = AsyncMock(return_value=[])
        
        # Act
        result = await player_service.get_players_by_session_id(session_id, None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        player_service.dao.get_players_by_session_id.assert_called_once_with(None, session_id)

    @pytest.mark.asyncio
    async def test_update_player_position_success(self, player_service, sample_player):
        """Тест успешного обновления позиции игрока."""
        # Arrange
        player_id = uuid4()
        new_cell_id = 10
        updated_player = MagicMock(
            id=player_id,
            cell_id=new_cell_id,
            previous_cell_id=sample_player.cell_id
        )
        player_service.update = AsyncMock(return_value=updated_player)
        
        # Act
        result = await player_service.update_player_position(player_id, new_cell_id, None)
        
        # Assert
        assert isinstance(result, PlayerResponse)
        assert result.cell_id == new_cell_id
        player_service.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_player_position_not_found(self, player_service):
        """Тест обновления позиции несуществующего игрока."""
        # Arrange
        player_id = uuid4()
        new_cell_id = 10
        player_service.update = AsyncMock(return_value=None)
        
        # Act
        result = await player_service.update_player_position(player_id, new_cell_id, None)
        
        # Assert
        assert result is None
        player_service.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_player_with_full_data_success(self, player_service, sample_player):
        """Тест получения игрока с полными данными."""
        # Arrange
        player_id = uuid4()
        player_service.get_by_id = AsyncMock(return_value=sample_player)
        
        # Act
        result = await player_service.get_player_with_full_data(player_id, None)
        
        # Assert
        assert isinstance(result, PlayerWithRelations)
        assert result.username == sample_player.username
        player_service.get_by_id.assert_called_once_with(player_id, None)

    @pytest.mark.asyncio
    async def test_get_player_with_full_data_not_found(self, player_service):
        """Тест получения несуществующего игрока с полными данными."""
        # Arrange
        player_id = uuid4()
        player_service.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await player_service.get_player_with_full_data(player_id, None)
        
        # Assert
        assert result is None
        player_service.get_by_id.assert_called_once_with(player_id, None)

    @pytest.mark.asyncio
    async def test_delete_player_success(self, player_service):
        """Тест успешного удаления игрока."""
        # Arrange
        player_id = uuid4()
        player_service.delete = AsyncMock(return_value=True)
        
        # Act
        result = await player_service.delete_player(player_id, None)
        
        # Assert
        assert result is True
        player_service.delete.assert_called_once_with(player_id, None)

    @pytest.mark.asyncio
    async def test_delete_player_not_found(self, player_service):
        """Тест удаления несуществующего игрока."""
        # Arrange
        player_id = uuid4()
        player_service.delete = AsyncMock(return_value=False)
        
        # Act
        result = await player_service.delete_player(player_id, None)
        
        # Assert
        assert result is False
        player_service.delete.assert_called_once_with(player_id, None)

    @pytest.mark.asyncio
    async def test_get_all_players_success(self, player_service, sample_player):
        """Тест получения всех игроков."""
        # Arrange
        players = [sample_player]
        player_service.get_all = AsyncMock(return_value=players)
        
        # Act
        result = await player_service.get_all_players(None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].username == sample_player.username
        player_service.get_all.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_get_all_players_empty(self, player_service):
        """Тест получения пустого списка игроков."""
        # Arrange
        player_service.get_all = AsyncMock(return_value=[])
        
        # Act
        result = await player_service.get_all_players(None)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        player_service.get_all.assert_called_once_with(None)
