from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from uuid import UUID

from src.services.game_manager_service import GameManagerService
from src.services.user_service import UserService
from src.services.player_service import PlayerService
from src.schemas.user import UserCreate, UserResponse
from src.schemas.player import PlayerCreate, PlayerResponse
from src.schemas.session import SessionCreate, SessionResponse

router = APIRouter(prefix="/api/v1", tags=["game"])

# Инициализируем сервисы
game_manager = GameManagerService()
user_service = UserService()
player_service = PlayerService()


@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate, player_data: PlayerCreate):
    """
    Регистрация пользователя и создание игрового профиля
    
    Пример правильного использования сервисов с декоратором @connection
    """
    try:
        result = await game_manager.register_and_create_profile(user_data, player_data)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, creator_id: UUID):
    """
    Создание новой игровой сессии
    """
    try:
        return await game_manager.start_game_session(creator_id, session_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sessions/{session_id}/join")
async def join_session(session_id: UUID, user_id: UUID):
    """
    Присоединение к игровой сессии
    """
    try:
        success = await game_manager.join_game_session(session_id, user_id)
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/game/turn")
async def play_turn(player_id: UUID, session_id: UUID):
    """
    Выполнение хода игрока
    """
    try:
        result = await game_manager.play_turn(player_id, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/players/{player_id}/dashboard")
async def get_player_dashboard(player_id: UUID):
    """
    Получение дашборда игрока
    """
    try:
        dashboard = await game_manager.get_player_dashboard(player_id)
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions/{session_id}/dashboard")
async def get_session_dashboard(session_id: UUID):
    """
    Получение дашборда сессии
    """
    try:
        dashboard = await game_manager.get_session_dashboard(session_id)
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/players/{player_id}/roll-dice")
async def roll_dice(player_id: UUID, modifiers: Dict[str, int] = None):
    """
    Бросок кубика для игрока
    """
    try:
        result = await player_service.roll_dice(player_id, modifiers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}")
async def get_user(user_id: UUID):
    """
    Получение пользователя по ID
    """
    try:
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") 