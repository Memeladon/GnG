import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserAuthResponse
from src.database.postgres.sql_enums import UserRights


class TestUserService:
    """Тесты для UserService по паттерну AAA (Arrange, Act, Assert)"""

    @pytest.fixture
    def user_service(self):
        """Создание экземпляра UserService для тестирования."""
        return UserService()

    @pytest.fixture
    def sample_user(self):
        """Тестовые данные пользователя."""
        return MagicMock(
            id=uuid4(),
            login="test_user",
            password="hashed_password",
            mail="test@example.com",
            is_active=True
        )

    @pytest.fixture
    def user_create_data(self):
        """Тестовые данные для создания пользователя."""
        return UserCreate(
            login="new_user",
            password="password123",
            mail="new@example.com"
        )

    @pytest.mark.asyncio
    async def test_register_user_success(self, user_service, user_create_data, sample_user):
        """Тест успешной регистрации пользователя."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=None)  # Пользователь не существует
        user_service.dao.create_user_unique = AsyncMock(return_value=sample_user)
        
        # Act
        result = await user_service.register_user(user_create_data, None)
        
        # Assert
        assert isinstance(result, UserResponse)
        assert result.login == sample_user.login
        assert result.mail == sample_user.mail
        assert result.is_active == sample_user.is_active
        user_service.dao.find_one_by.assert_called_once_with(None, login=user_create_data.login)
        user_service.dao.create_user_unique.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, user_service, user_create_data):
        """Тест регистрации пользователя, который уже существует."""
        # Arrange
        existing_user = MagicMock(login="new_user")
        user_service.dao.find_one_by = AsyncMock(return_value=existing_user)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Пользователь с логином 'new_user' уже существует"):
            await user_service.register_user(user_create_data, None)
        
        user_service.dao.find_one_by.assert_called_once_with(None, login=user_create_data.login)
        user_service.dao.create_user_unique.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_service, sample_user):
        """Тест успешной аутентификации пользователя."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=sample_user)
        
        # Act
        result = await user_service.authenticate_user("test_user", "password123", None)
        
        # Assert
        assert isinstance(result, UserAuthResponse)
        assert result.user.login == sample_user.login
        assert result.access_token is not None
        assert result.token_type == "bearer"
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_service):
        """Тест аутентификации несуществующего пользователя."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=None)
        
        # Act
        result = await user_service.authenticate_user("nonexistent", "password123", None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_called_once_with(None, login="nonexistent")

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, user_service):
        """Тест аутентификации неактивного пользователя."""
        # Arrange
        inactive_user = MagicMock(
            login="test_user",
            password="hashed_password",
            is_active=False
        )
        user_service.dao.find_one_by = AsyncMock(return_value=inactive_user)
        
        # Act
        result = await user_service.authenticate_user("test_user", "password123", None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, user_service, sample_user):
        """Тест аутентификации с неправильным паролем."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=sample_user)
        # Мокаем _verify_password чтобы вернуть False
        user_service._verify_password = MagicMock(return_value=False)
        
        # Act
        result = await user_service.authenticate_user("test_user", "wrong_password", None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")
        user_service._verify_password.assert_called_once_with("wrong_password", "hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user_simple_success(self, user_service, sample_user):
        """Тест простой аутентификации пользователя."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=sample_user)
        
        # Act
        result = await user_service.authenticate_user_simple("test_user", "password123", None)
        
        # Assert
        assert isinstance(result, UserResponse)
        assert result.login == sample_user.login
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    @pytest.mark.asyncio
    async def test_get_user_by_login_success(self, user_service, sample_user):
        """Тест получения пользователя по логину."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=sample_user)
        
        # Act
        result = await user_service.get_user_by_login("test_user", None)
        
        # Assert
        assert isinstance(result, UserResponse)
        assert result.login == sample_user.login
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    @pytest.mark.asyncio
    async def test_get_user_by_login_not_found(self, user_service):
        """Тест получения несуществующего пользователя по логину."""
        # Arrange
        user_service.dao.find_one_by = AsyncMock(return_value=None)
        
        # Act
        result = await user_service.get_user_by_login("nonexistent", None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_called_once_with(None, login="nonexistent")

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, user_service, sample_user):
        """Тест успешного обновления профиля пользователя."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(username="new_username", mail="new@example.com")
        updated_user = MagicMock(
            id=user_id,
            login="test_user",
            username="new_username",
            mail="new@example.com",
            is_active=True
        )
        user_service.dao.update_one = AsyncMock(return_value=updated_user)
        
        # Act
        result = await user_service.update_user_profile(user_id, update_data, None)
        
        # Assert
        assert isinstance(result, UserResponse)
        assert result.username == "new_username"
        assert result.mail == "new@example.com"
        user_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self, user_service):
        """Тест обновления профиля несуществующего пользователя."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(username="new_username")
        user_service.dao.update_one = AsyncMock(return_value=None)
        
        # Act
        result = await user_service.update_user_profile(user_id, update_data, None)
        
        # Assert
        assert result is None
        user_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_success(self, user_service, sample_user):
        """Тест успешной смены пароля."""
        # Arrange
        user_id = uuid4()
        old_password = "old_password"
        new_password = "new_password"
        updated_user = MagicMock(id=user_id)
        
        user_service.dao.get_by_id = AsyncMock(return_value=sample_user)
        user_service.dao.update_one = AsyncMock(return_value=updated_user)
        
        # Act
        result = await user_service.change_password(user_id, old_password, new_password, None)
        
        # Assert
        assert result is True
        user_service.dao.get_by_id.assert_called_once_with(None, user_id)
        user_service.dao.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, user_service):
        """Тест смены пароля несуществующего пользователя."""
        # Arrange
        user_id = uuid4()
        user_service.dao.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await user_service.change_password(user_id, "old", "new", None)
        
        # Assert
        assert result is False
        user_service.dao.get_by_id.assert_called_once_with(None, user_id)
        user_service.dao.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, user_service, sample_user):
        """Тест смены пароля с неправильным старым паролем."""
        # Arrange
        user_id = uuid4()
        user_service.dao.get_by_id = AsyncMock(return_value=sample_user)
        user_service._verify_password = MagicMock(return_value=False)
        
        # Act
        result = await user_service.change_password(user_id, "wrong_old", "new", None)
        
        # Assert
        assert result is False
        user_service.dao.get_by_id.assert_called_once_with(None, user_id)
        user_service._verify_password.assert_called_once_with("wrong_old", "hashed_password")
        user_service.dao.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, user_service):
        """Тест деактивации пользователя."""
        # Arrange
        user_id = uuid4()
        user_service.update = AsyncMock(return_value=MagicMock())
        
        # Act
        result = await user_service.deactivate_user(user_id, None)
        
        # Assert
        assert result is True
        user_service.update.assert_called_once_with(None, {"id": user_id, "is_active": False})

    @pytest.mark.asyncio
    async def test_activate_user_success(self, user_service):
        """Тест активации пользователя."""
        # Arrange
        user_id = uuid4()
        user_service.update = AsyncMock(return_value=MagicMock())
        
        # Act
        result = await user_service.activate_user(user_id, None)
        
        # Assert
        assert result is True
        user_service.update.assert_called_once_with(None, {"id": user_id, "is_active": True})

    @pytest.mark.asyncio
    async def test_get_user_with_relations_success(self, user_service, sample_user):
        """Тест получения пользователя со связанными данными."""
        # Arrange
        user_id = uuid4()
        user_service.dao.get_one = AsyncMock(return_value=sample_user)
        
        # Act
        result = await user_service.get_user_with_relations(user_id, None)
        
        # Assert
        assert result == sample_user
        user_service.dao.get_one.assert_called_once_with(None, user_id)

    @pytest.mark.asyncio
    async def test_get_user_with_relations_not_found(self, user_service):
        """Тест получения несуществующего пользователя со связанными данными."""
        # Arrange
        user_id = uuid4()
        user_service.dao.get_one = AsyncMock(return_value=None)
        
        # Act
        result = await user_service.get_user_with_relations(user_id, None)
        
        # Assert
        assert result is None
        user_service.dao.get_one.assert_called_once_with(None, user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_token_success(self, user_service, sample_user):
        """Тест получения пользователя по токену."""
        # Arrange
        token = "valid_token"
        user_service.dao.find_one_by = AsyncMock(return_value=sample_user)
        
        # Act
        result = await user_service.get_user_by_token(token, None)
        
        # Assert
        assert isinstance(result, UserResponse)
        assert result.login == sample_user.login
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    @pytest.mark.asyncio
    async def test_get_user_by_token_invalid_token(self, user_service):
        """Тест получения пользователя по невалидному токену."""
        # Arrange
        token = "invalid_token"
        
        # Act
        result = await user_service.get_user_by_token(token, None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_by_token_user_not_found(self, user_service):
        """Тест получения пользователя по токену, когда пользователь не найден."""
        # Arrange
        token = "valid_token"
        user_service.dao.find_one_by = AsyncMock(return_value=None)
        
        # Act
        result = await user_service.get_user_by_token(token, None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    @pytest.mark.asyncio
    async def test_get_user_by_token_inactive_user(self, user_service):
        """Тест получения неактивного пользователя по токену."""
        # Arrange
        token = "valid_token"
        inactive_user = MagicMock(
            login="test_user",
            is_active=False
        )
        user_service.dao.find_one_by = AsyncMock(return_value=inactive_user)
        
        # Act
        result = await user_service.get_user_by_token(token, None)
        
        # Assert
        assert result is None
        user_service.dao.find_one_by.assert_called_once_with(None, login="test_user")

    def test_hash_password(self, user_service):
        """Тест хеширования пароля."""
        # Arrange
        password = "test_password"
        
        # Act
        result = user_service._hash_password(password)
        
        # Assert
        assert isinstance(result, str)
        assert result != password

    def test_verify_password_success(self, user_service):
        """Тест успешной проверки пароля."""
        # Arrange
        password = "test_password"
        hashed_password = user_service._hash_password(password)
        
        # Act
        result = user_service._verify_password(password, hashed_password)
        
        # Assert
        assert result is True

    def test_verify_password_failure(self, user_service):
        """Тест неуспешной проверки пароля."""
        # Arrange
        password = "test_password"
        wrong_password = "wrong_password"
        hashed_password = user_service._hash_password(password)
        
        # Act
        result = user_service._verify_password(wrong_password, hashed_password)
        
        # Assert
        assert result is False

    def test_create_access_token(self, user_service):
        """Тест создания токена доступа."""
        # Arrange
        username = "test_user"
        
        # Act
        result = user_service.create_access_token(username)
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
