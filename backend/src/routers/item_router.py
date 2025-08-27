from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel

from src.services.inventory_service import InventoryService
from src.services.user_service import UserService
from src.database.postgres.dao.base import connection

router = APIRouter(prefix="/items", tags=["items"])

# Pydantic модели для запросов
class UseItemRequest(BaseModel):
    target_player_id: Optional[UUID] = None
    new_dice_value: Optional[int] = None
    target_item_id: Optional[int] = None
    game_id: Optional[int] = None
    coin_side: Optional[str] = None
    selected_game: Optional[str] = None
    cell_id: Optional[int] = None
    use_type: Optional[str] = None
    trap_item_id: Optional[int] = None
    bonus_type: Optional[str] = None
    previous_cell_id: Optional[int] = None
    dice_values: Optional[List[int]] = None
    wheel_item: Optional[str] = None
    dice_value: Optional[int] = None
    unwanted_item: Optional[str] = None
    desired_item: Optional[str] = None

class AddItemRequest(BaseModel):
    inventory_id: int
    item_id: int
    uses: int = 1
    custom_state: Optional[str] = None

# Зависимости
def get_inventory_service() -> InventoryService:
    return InventoryService()

def get_user_service() -> UserService:
    return UserService()

# Роуты
@router.get("/inventory/{player_id}")
async def get_inventory_items(
    player_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> List[Dict[str, Any]]:
    """Получение всех предметов в инвентаре игрока"""
    try:
        items = await inventory_service.get_player_inventory_items(player_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении инвентаря: {str(e)}")

@router.post("/use/{item_instance_id}")
async def use_item(
    item_instance_id: int,
    player_id: UUID,
    request: UseItemRequest,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Использование предмета"""
    try:
        # Используем предмет
        result = await inventory_service.use_item_with_logic(
            item_instance_id=item_instance_id,
            player_id=player_id,
            target_player_id=request.target_player_id,
            **request.dict(exclude_none=True)
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Ошибка использования предмета"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при использовании предмета: {str(e)}")

@router.post("/add")
async def add_item_to_inventory(
    request: AddItemRequest,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Добавление предмета в инвентарь"""
    try:
        result = await inventory_service.add_item_with_logic(
            inventory_id=request.inventory_id,
            item_id=request.item_id,
            uses=request.uses,
            custom_state=request.custom_state
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Ошибка добавления предмета"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении предмета: {str(e)}")

@router.delete("/{item_instance_id}")
async def remove_item_from_inventory(
    item_instance_id: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Удаление предмета из инвентаря"""
    try:
        result = await inventory_service.remove_item_with_logic(item_instance_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Ошибка удаления предмета"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении предмета: {str(e)}")



# Специальные роуты для сложных предметов

@router.post("/chocolate/combine")
async def combine_chocolate(
    player_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Попытка объединения шоколада в плитку"""
    try:
        # Получаем инвентарь игрока
        items = await inventory_service.get_player_inventory_items(player_id)
        chocolate_items = [item for item in items if item["title"] == "Шоколад"]
        
        if len(chocolate_items) >= 4:
            # Удаляем все шоколады и создаем плитку
            # Это будет обработано в on_acquire при добавлении нового шоколада
            return {"success": True, "message": "Достаточно шоколада для создания плитки"}
        else:
            return {"success": False, "message": f"Недостаточно шоколада. Нужно: 4, есть: {len(chocolate_items)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при объединении шоколада: {str(e)}")

@router.post("/rings/link")
async def link_time_rings(
    item_instance_id: int,
    player_id: UUID,
    target_player_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Связывание парных колец времени"""
    try:
        result = await inventory_service.use_item_with_logic(
            item_instance_id=item_instance_id,
            player_id=player_id,
            target_player_id=target_player_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при связывании колец: {str(e)}")

@router.post("/rings/use-effect")
async def use_time_ring_effect(
    item_instance_id: int,
    player_id: UUID,
    cell_id: int,
    item_service: ItemInstanceService = Depends(get_item_service)
) -> Dict[str, Any]:
    """Использование эффекта кольца времени"""
    try:
        # Этот метод требует специальной обработки в сервисе
        # Пока возвращаем заглушку
        return {"success": True, "message": "Эффект кольца времени применен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при использовании эффекта кольца: {str(e)}")

@router.post("/fisting/transfer-points")
async def transfer_fisting_points(
    slave_player_id: UUID,
    points_earned: int,
    item_service: ItemInstanceService = Depends(get_item_service)
) -> Dict[str, Any]:
    """Передача очков через руку fisting"""
    try:
        # Этот метод требует специальной обработки в сервисе
        # Пока возвращаем заглушку
        return {"success": True, "message": f"Передано {points_earned // 5} очков"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при передаче очков: {str(e)}")

# Роуты для событий колеса (не предметы)

@router.post("/wheel/reroll")
async def wheel_reroll(
    player_id: UUID
) -> Dict[str, Any]:
    """Реролл колеса приколов"""
    try:
        # Здесь должна быть логика реролла колеса
        return {"success": True, "message": "Колесо перекручено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при реролле колеса: {str(e)}")

@router.post("/wheel/two-for-one")
async def wheel_two_for_one(
    player_id: UUID
) -> Dict[str, Any]:
    """Два по цене одного"""
    try:
        # Здесь должна быть логика выполнения двух соседних пунктов
        return {"success": True, "message": "Выполнены два соседних пункта"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении двух пунктов: {str(e)}")

@router.post("/wheel/chat-choice")
async def wheel_chat_choice(
    player_id: UUID
) -> Dict[str, Any]:
    """По магазинам с чатом"""
    try:
        # Здесь должна быть логика выбора чатом
        return {"success": True, "message": "Чат выбрал пункт"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выборе чатом: {str(e)}")

@router.post("/wheel/leprechaun-choice")
async def wheel_leprechaun_choice(
    player_id: UUID
) -> Dict[str, Any]:
    """По магазинам с Лепреконом"""
    try:
        # Здесь должна быть логика выбора судьей
        return {"success": True, "message": "Судья выбрал пункт"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выборе судьей: {str(e)}")

@router.post("/wheel/one-armed-bandit")
async def wheel_one_armed_bandit(
    player_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Однорукий бандит - сброс всех предметов"""
    try:
        # Получаем все предметы игрока
        items = await inventory_service.get_player_inventory_items(player_id)
        
        # Удаляем все предметы
        for item in items:
            await inventory_service.remove_item_with_logic(item["id"])
        
        return {
            "success": True, 
            "message": f"Сброшено {len(items)} предметов",
            "items_dropped": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сбросе предметов: {str(e)}")

@router.post("/wheel/dirty-boy")
async def wheel_dirty_boy(
    player_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Грязнулькин - съедает случайный бафф"""
    try:
        # Получаем все предметы игрока
        items = await inventory_service.get_player_inventory_items(player_id)
        buff_items = [item for item in items if item["type"] == "Бафф"]
        
        if buff_items:
            # Удаляем случайный бафф
            import random
            random_buff = random.choice(buff_items)
            await inventory_service.remove_item_with_logic(random_buff["id"])
            
            return {
                "success": True,
                "message": f"Съеден бафф: {random_buff['title']}",
                "eaten_item": random_buff["title"]
            }
        else:
            return {"success": False, "message": "Нет баффов для съедения"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при съедении баффа: {str(e)}")

@router.post("/wheel/swap-inventories")
async def wheel_swap_inventories(
    player_id: UUID,
    target_player_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> Dict[str, Any]:
    """Mine now TriHard - обмен инвентарями"""
    try:
        # Получаем предметы обоих игроков
        player_items = await inventory_service.get_player_inventory_items(player_id)
        target_items = await inventory_service.get_player_inventory_items(target_player_id)
        
        # Здесь должна быть логика обмена инвентарями
        # Это сложная операция, требующая специальной реализации
        
        return {
            "success": True,
            "message": "Инвентари обменены",
            "player_items_count": len(player_items),
            "target_items_count": len(target_items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обмене инвентарями: {str(e)}") 