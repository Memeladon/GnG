import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.database.postgres.models import Base
from src.database.postgres.sql_enums import UserRights, ItemType, EffectType, EffectCategory, GameStatus
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.player import PlayerCreate, PlayerUpdate
from src.schemas.item import ItemCreate
from src.schemas.item_instance import ItemInstanceCreate
from src.schemas.inventory import InventoryCreate
from src.schemas.player_effects import PlayerEffectsCreate
from src.schemas.game import GameCreate


# Test database configuration
# Can be overridden via environment variable TEST_DATABASE_URL
# Example: postgresql+asyncpg://postgres:postgres@localhost:5432/monopoly_test
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/monopoly_test",
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False
    )
    
    async with engine.begin() as conn:
        # Ensure a clean schema for tests
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


# Mock fixtures for external dependencies
@pytest.fixture
def mock_crypto():
    """Mock crypto functions."""
    mock = MagicMock()
    mock.pwd_context.hash.return_value = "hashed_password"
    mock.verify.return_value = True
    mock.create_access_token.return_value = "test_token"
    mock.get_current_user.return_value = {"username": "test_user"}
    return mock


@pytest.fixture
def mock_logger():
    """Mock logger."""
    mock = MagicMock()
    mock.info = MagicMock()
    mock.error = MagicMock()
    mock.warning = MagicMock()
    return mock


# Test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": uuid4(),
        "login": "test_user",
        "password": "test_password",
        "mail": "test@example.com",
        "is_active": True
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "id": uuid4(),
        "user_id": uuid4(),
        "username": "test_player",
        "profile_image": "test_avatar.png",
        "cell_id": 0,
        "role": UserRights.PLAYER,
        "dice_modifier": 0,
        "game_modifier": 0,
        "last_dice_value": 0,
        "previous_cell_id": 0
    }


@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "id": 1,
        "title": "Читерский кубик",
        "description": "Позволяет заменить значение кубика",
        "item_image": "cheat_dice.png",
        "type": ItemType.MODIFIER,
        "uses": None,
        "modifier_turns": None
    }


@pytest.fixture
def sample_item_instance_data():
    """Sample item instance data for testing."""
    return {
        "id": 1,
        "item_id": 1,
        "inventory_id": 1,
        "uses": 3,
        "modifier_turns": None
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return {
        "id": 1,
        "player_id": uuid4()
    }


@pytest.fixture
def sample_effect_data():
    """Sample player effect data for testing."""
    return {
        "id": 1,
        "player_id": uuid4(),
        "effect_name": "ez_difficulty",
        "effect_type": EffectType.BUFF,
        "effect_category": EffectCategory.GAME_MODIFIER,
        "turns_remaining": 2,
        "is_active": True,
        "effect_data": {},
        "item_instance_id": 1
    }


@pytest.fixture
def sample_game_data():
    """Sample game data for testing."""
    return {
        "id": 1,
        "player_id": uuid4(),
        "status": GameStatus.PROGRESS,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "review": "Great game!",
        "points": 85,
        "hours": 2.5
    }


# Schema fixtures
@pytest.fixture
def user_create_schema():
    """UserCreate schema for testing."""
    return UserCreate(
        login="test_user",
        password="test_password",
        mail="test@example.com"
    )


@pytest.fixture
def player_create_schema():
    """PlayerCreate schema for testing."""
    return PlayerCreate(
        user_id=uuid4(),
        username="test_player",
        profile_image="test_avatar.png",
        role=UserRights.PLAYER,
        cell_id=0,
        inventory_id=1
    )


@pytest.fixture
def item_create_schema():
    """ItemCreate schema for testing."""
    return ItemCreate(
        title="Читерский кубик",
        description="Позволяет заменить значение кубика",
        type=ItemType.MODIFIER
    )


@pytest.fixture
def item_instance_create_schema():
    """ItemInstanceCreate schema for testing."""
    return ItemInstanceCreate(
        item_id=1,
        inventory_id=1,
        uses=3
    )


@pytest.fixture
def inventory_create_schema():
    """InventoryCreate schema for testing."""
    return InventoryCreate(
        player_id=uuid4()
    )


@pytest.fixture
def player_effects_create_schema():
    """PlayerEffectsCreate schema for testing."""
    return PlayerEffectsCreate(
        player_id=uuid4(),
        effect_name="ez_difficulty",
        effect_type=EffectType.BUFF,
        effect_category=EffectCategory.GAME_MODIFIER,
        turns_remaining=2,
        item_instance_id=1
    )


@pytest.fixture
def game_create_schema():
    """GameCreate schema for testing."""
    return GameCreate(
        player_id=uuid4(),
        status=GameStatus.PROGRESS,
        review="Great game!",
        points=85,
        hours=2.5
    )


# Service fixtures
@pytest.fixture
def mock_user_dao():
    """Mock UserDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.create_user_unique = AsyncMock()
    return mock


@pytest.fixture
def mock_player_dao():
    """Mock PlayerDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.create_player_first_time = AsyncMock()
    mock.update_player_profile = AsyncMock()
    mock.get_players_by_session_id = AsyncMock()
    return mock


@pytest.fixture
def mock_item_dao():
    """Mock ItemDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    return mock


@pytest.fixture
def mock_item_instance_dao():
    """Mock ItemInstanceDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.use_item = AsyncMock()
    return mock


@pytest.fixture
def mock_inventory_dao():
    """Mock InventoryDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.is_inventory_full = AsyncMock()
    mock.add_item_to_inventory = AsyncMock()
    mock.replace_item_in_inventory = AsyncMock()
    mock.search_items_in_inventory = AsyncMock()
    return mock


@pytest.fixture
def mock_player_effects_dao():
    """Mock PlayerEffectsDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.get_many = AsyncMock()
    return mock


@pytest.fixture
def mock_game_dao():
    """Mock GameDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    return mock


@pytest.fixture
def mock_cell_dao():
    """Mock CellDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.add_trap_to_cell = AsyncMock()
    mock.remove_trap_from_cell = AsyncMock()
    mock.get_cell_traps = AsyncMock()
    return mock


@pytest.fixture
def mock_session_dao():
    """Mock SessionDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.close_session = AsyncMock()
    mock.is_session_expired = AsyncMock()
    mock.get_sessions_by_user_id = AsyncMock()
    return mock


@pytest.fixture
def mock_session_user_dao():
    """Mock SessionUserDAO."""
    mock = AsyncMock()
    mock.create_one = AsyncMock()
    mock.get_one = AsyncMock()
    mock.find_one_by = AsyncMock()
    mock.exists_by = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.add_user_to_session = AsyncMock()
    mock.get_session_users_with_user_data = AsyncMock()
    return mock
