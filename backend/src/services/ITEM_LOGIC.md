# Логика работы предметов колеса приколов

## Общая архитектура

### Модели данных:
- **Item** - оригиналы предметов (неизменяемые шаблоны)
- **ItemInstance** - экземпляры предметов в инвентаре игроков
- **PlayerEffects** - активные эффекты игроков (связаны с ItemInstance через item_instance_id)

### Сервисы:
- **InventoryService** - управление инвентарем и использование предметов
- **ItemInstanceService** - логика использования конкретных предметов
- **EffectsService** - управление эффектами игроков

### DAO слои:
- **InventoryDAO** - операции с инвентарем
- **ItemInstanceDAO** - операции с экземплярами предметов
- **PlayerEffectsDAO** - операции с эффектами игроков
- **PlayerDAO** - операции с игроками
- **ItemDAO** - операции с предметами

### Архитектурные слои:
```
API/Router → Service → DAO → Database
```

**Пример вызова:**
```
Router.use_item() 
→ InventoryService.use_item() 
→ PlayerDAO.get_one() 
→ ItemInstanceDAO.get_one() 
→ ItemInstanceService._use_item_by_title() 
→ ItemInstanceDAO.use_item() 
→ Database
```

### Жизненный цикл эффектов:
- **Бесконечные эффекты** (turns_remaining=None): активны пока предмет в инвентаре
- **Временные эффекты** (turns_remaining>0): уменьшаются на 1 при завершении игры
- **Эффекты от использованных предметов**: удаляются при завершении игры



---

## Предметы с бесконечными эффектами

### 1. Шар всезнания

**Описание**: Разрешает использование гайда или видеопрохождения.

**Метод ItemInstanceService**: `_use_knowledge_sphere()` - просто использует предмет (эффект уже активен с момента получения)

**Логика работы**:

#### При получении предмета:
```python
# InventoryService.add_item_to_inventory()
# → InventoryDAO.add_item_to_inventory()
# → ItemInstanceDAO.create_one()
# → ItemInstanceService._on_acquire_knowledge_sphere()
# → EffectsService.add_player_effect()
# → PlayerEffectsDAO.create_one()

await effects_service.add_player_effect(
    player_id=player.id,
    effect_name="allow_guide",
    effect_type=EffectType.BUFF,
    effect_category=EffectCategory.GAME_MODIFIER,
    turns_remaining=None,  # Бесконечный эффект
    item_instance_id=item_instance.id,  # Связь с экземпляром
    session=session
)
```



#### При использовании предмета:
```python
# InventoryService.use_item()
# → PlayerDAO.get_one() - получение игрока
# → ItemInstanceDAO.get_one() - получение экземпляра предмета
# → ItemInstanceService._check_effect_conflicts() - проверка конфликтов
# → ItemInstanceService._use_item_by_title()
# → ItemInstanceService._use_knowledge_sphere()
# → ItemInstanceDAO.use_item() - уменьшение uses или удаление
await ItemInstanceDAO.use_item(session, item_instance.id)
# ItemInstance удаляется, но эффект остается до конца хода
```



#### При завершении игры:
```python
# EffectsService.on_game_completed()
# → PlayerEffectsDAO.get_many() - получение всех активных эффектов игрока
effects = await PlayerEffectsDAO.get_many(session, {"player_id": player_id, "is_active": True})
for effect in effects:
    if effect.item_instance_id:
        # → ItemInstanceDAO.get_one() - проверка существования экземпляра предмета
        item_instance = await ItemInstanceDAO.get_one(session, effect.item_instance_id)
        if not item_instance:  # ItemInstance не существует (был использован)
            # → PlayerEffectsDAO.delete_one() - удаление эффекта
            await PlayerEffectsDAO.delete_one(session, effect.id)
```



---

### 2. Красочная манга

**Описание**: Разрешает прохождение визуальныйх новел, но запрещает автоскип в них.

**Метод ItemInstanceService**: `_use_colorful_manga()` - просто использует предмет (эффект уже активен с момента получения)

**Логика работы**:

#### При получении предмета:
```python
# InventoryService.add_item_to_inventory()
# → InventoryDAO.add_item_to_inventory()
# → ItemInstanceDAO.create_one()
# → ItemInstanceService._on_acquire_colorful_manga()
# → EffectsService.add_player_effect()
# → PlayerEffectsDAO.create_one()

await effects_service.add_player_effect(
    player_id=player.id,
    effect_name="visual_novel_no_skip",
    effect_type=EffectType.BUFF,
    effect_category=EffectCategory.GAME_MODIFIER,
    turns_remaining=None,  # Бесконечный эффект
    item_instance_id=item_instance.id,
    session=session
)
```

#### При использовании предмета:
```python
# InventoryService.use_item()
# → PlayerDAO.get_one() - получение игрока
# → ItemInstanceDAO.get_one() - получение экземпляра предмета
# → ItemInstanceService._use_item_by_title()
# → ItemInstanceService._use_colorful_manga()
# → ItemInstanceDAO.use_item() - уменьшение uses или удаление
await ItemInstanceDAO.use_item(session, item_instance.id)
# Эффект сохраняется до конца хода
```

#### При завершении игры:
```python
# EffectsService.on_game_completed()
# Эффект удаляется если ItemInstance не существует
```

---

## Предметы с временными эффектами

### 3. Очки EZ

**Описание**: Следующие 2 хода игры на легком уровне сложности.

**Метод ItemInstanceService**: `_use_ez_glasses()` - добавляет эффект "ez_difficulty" на 2 хода, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# InventoryService.use_item()
# → PlayerDAO.get_one() - получение игрока
# → ItemInstanceDAO.get_one() - получение экземпляра предмета
# → ItemInstanceService._use_item_by_title()
# → ItemInstanceService._use_ez_glasses()
# → EffectsService.add_player_effect()
# → PlayerEffectsDAO.create_one()
await self.effects_service.add_player_effect(
    player_id=player.id,
    effect_name="ez_difficulty",
    effect_type=EffectType.BUFF,
    effect_category=EffectCategory.GAME_MODIFIER,
    turns_remaining=2,  # 2 хода
    session=session
)
# → ItemInstanceDAO.use_item() - уменьшение uses или удаление
await ItemInstanceDAO.use_item(session, item_instance.id)
```



#### При завершении игры:
```python
# EffectsService.on_game_completed()
# → EffectsService.decrement_effect_turns()
# → PlayerEffectsDAO.get_many() - получение всех активных эффектов
for effect in effects:
    if effect.turns_remaining is not None and effect.turns_remaining > 0:
        effect.turns_remaining -= 1
        if effect.turns_remaining <= 0:
            # → PlayerEffectsDAO.delete_one() - удаление истекшего эффекта
            await PlayerEffectsDAO.delete_one(session, effect.id)
        else:
            # → PlayerEffectsDAO.update_one() - обновление оставшихся ходов
            await PlayerEffectsDAO.update_one(session, {
                "id": effect.id,
                "turns_remaining": effect.turns_remaining
            })
```



---

### 4. Повязка Рэмбо

**Описание**: Следующие 2 хода игры на высоком уровне сложности.

**Метод ItemInstanceService**: `_use_rambo_bandana()` - добавляет эффект "rambo_difficulty" на 2 хода, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_rambo_bandana()
await self.effects_service.add_player_effect(
    player_id=player.id,
    effect_name="rambo_difficulty",
    effect_type=EffectType.DEBUFF,
    effect_category=EffectCategory.GAME_MODIFIER,
    turns_remaining=2,  # 2 хода
    session=session
)
await ItemInstanceDAO.use_item(session, item_instance.id)
```

---

### 5. Тотем мошны

**Описание**: Защита от ловушек-событий на 2 хода.

**Метод ItemInstanceService**: `_use_mohsna_totem()` - добавляет эффект "trap_protection" на 2 хода

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_mohsna_totem()
await self.effects_service.add_player_effect(
    player_id=player.id,
    effect_name="trap_protection",
    effect_type=EffectType.BUFF,
    effect_category=EffectCategory.PROTECTION,
    turns_remaining=2,  # 2 хода
    session=session
)
```

---

## Предметы с эффектами на других игроков

### 6. Тухлая шаурма (ловушка)

**Описание**: -1 к кубикам на 2 хода для целевого игрока.

**Метод ItemInstanceService**: `_use_rotten_shawarma()` - добавляет эффект "rotten_shawarma" целевому игроку на 2 хода, удаляет ловушку

**Логика работы**:

#### При использовании предмета:
```python
# InventoryService.use_item()
# → PlayerDAO.get_one() - получение игрока
# → ItemInstanceDAO.get_one() - получение экземпляра предмета
# → ItemInstanceService._use_item_by_title()
# → ItemInstanceService._use_rotten_shawarma()
# → EffectsService.add_player_effect()
# → PlayerEffectsDAO.create_one() - создание эффекта для целевого игрока
if not target_player:
    return {"success": False, "message": "Не указан целевой игрок"}

await self.effects_service.add_player_effect(
    player_id=target_player.id,  # Эффект на целевого игрока
    effect_name="rotten_shawarma",
    effect_type=EffectType.DEBUFF,
    effect_category=EffectCategory.MOVEMENT,
    turns_remaining=2,
    effect_data={"dice_penalty": 1},
    session=session
)

# → ItemInstanceDAO.delete_one() - удаление ловушки
await ItemInstanceDAO.delete_one(session, item_instance.id)  # Ловушка удаляется
```



---

### 7. Чокер боли (ловушка)

**Описание**: Следующая игра только по жанровым правилам для целевого игрока.

**Метод ItemInstanceService**: `_use_pain_choker()` - добавляет эффект "pain_choker" целевому игроку на 1 ход, удаляет ловушку

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_pain_choker()
await self.effects_service.add_player_effect(
    player_id=target_player.id,
    effect_name="pain_choker",
    effect_type=EffectType.DEBUFF,
    effect_category=EffectCategory.GAME_MODIFIER,
    turns_remaining=1,  # 1 ход
    effect_data={"genre_rules_only": True},
    session=session
)

await ItemInstanceDAO.delete_one(session, item_instance.id)
```

---

### 8. Полукаловая монетка (ловушка)

**Описание**: На следующей клетке с временем подбрасывается монетка для целевого игрока.

**Метод ItemInstanceService**: `_use_half_penny()` - добавляет эффект "half_penny" целевому игроку на 1 ход, удаляет ловушку

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_half_penny()
await self.effects_service.add_player_effect(
    player_id=target_player.id,
    effect_name="half_penny",
    effect_type=EffectType.NEUTRAL,
    effect_category=EffectCategory.TIME_MODIFIER,
    turns_remaining=1,
    effect_data={"coin_flip": True},
    session=session
)

await ItemInstanceDAO.delete_one(session, item_instance.id)
```

---

## Предметы с эффектами на клетки

### 9. Штрафная квитанция

**Описание**: На следующей клетке с временем время увеличивается на 3 часа.

**Метод ItemInstanceService**: `_use_penalty_receipt()` - добавляет эффект "penalty_receipt" на 1 ход, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_penalty_receipt()
await self.effects_service.add_player_effect(
    player_id=player.id,  # Эффект на самого игрока
    effect_name="penalty_receipt",
    effect_type=EffectType.DEBUFF,
    effect_category=EffectCategory.TIME_MODIFIER,
    turns_remaining=1,
    effect_data={"time_increase": 3},
    session=session
)

await ItemInstanceDAO.use_item(session, item_instance.id)
```

---

## Предметы с мгновенными эффектами

### 10. Читерский кубик

**Описание**: Заменяет значение кубика на выбранное.

**Метод ItemInstanceService**: `_use_cheat_dice()` - устанавливает модификатор кубика для игрока, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# InventoryService.use_item()
# → PlayerDAO.get_one() - получение игрока
# → ItemInstanceDAO.get_one() - получение экземпляра предмета
# → ItemInstanceService._use_item_by_title()
# → ItemInstanceService._use_cheat_dice()
# → PlayerService.update_player()
# → PlayerDAO.update_one() - обновление модификатора кубика
new_dice_value = kwargs.get('new_dice_value')
if not new_dice_value:
    return {"success": False, "message": "Не указано новое значение кубика"}

await self.player_service.update_player(player.id, {"dice_modifier": new_dice_value})
# → ItemInstanceDAO.use_item() - уменьшение uses или удаление
await ItemInstanceDAO.use_item(session, item_instance.id)
```



---

### 11. Кубик хуюбика

**Описание**: При следующем броске большее значение заменяется на 1.

**Метод ItemInstanceService**: `_use_huybik_dice()` - устанавливает модификатор кубика в 1 и game_modifier в "huybik_dice"

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_huybik_dice()
await self.player_service.update_player(player.id, {
    "dice_modifier": 1, 
    "game_modifier": "huybik_dice"
})
await ItemInstanceDAO.use_item(session, item_instance.id)
```

---

### 12. Свиток реролла

**Описание**: Перезапускает игру.

**Метод ItemInstanceService**: `_use_reroll_scroll()` - вызывает reroll_game, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_reroll_scroll()
game_id = kwargs.get('game_id')
if not game_id:
    return {"success": False, "message": "Не указан ID игры для реролла"}

result = await self.game_service.reroll_game(game_id)
await ItemInstanceDAO.use_item(session, item_instance.id)
```

---

### 13. Взрывчатка

**Описание**: При использовании положительных свойств предметов бросается монетка.

**Метод ItemInstanceService**: `_use_explosive()` - использует предмет, возвращает результат броска монетки

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_explosive()
coin_side = kwargs.get('coin_side')
if not coin_side:
    return {"success": False, "message": "Не указана сторона монетки"}

await ItemInstanceDAO.use_item(session, item_instance.id)

if coin_side == 'heads':
    return {"success": True, "message": "Эффект сработал", "effect_active": True}
else:
    return {"success": True, "message": "Эффект не сработал", "effect_active": False}
```

---

### 14. Корона колесного короля

**Описание**: Выбор между двумя соседними играми.

**Метод ItemInstanceService**: `_use_wheel_crown()` - использует предмет, возвращает информацию о выбранной игре

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_wheel_crown()
selected_game = kwargs.get('selected_game')
if not selected_game:
    return {"success": False, "message": "Не выбрана игра"}

await ItemInstanceDAO.use_item(session, item_instance.id)
return {"success": True, "message": f"Выбрана игра: {selected_game}", "selected_game": selected_game}
```

---

### 15. Ремонтный набор

**Описание**: Увеличивает количество зарядов у предмета на 1.

**Метод ItemInstanceService**: `_use_repair_kit()` - увеличивает uses целевого предмета на 1, затем использует ремонтный набор

**Логика работы**:

#### При использовании предмета:
```python
# InventoryService.use_item()
# → PlayerDAO.get_one() - получение игрока
# → ItemInstanceDAO.get_one() - получение экземпляра предмета
# → ItemInstanceService._use_item_by_title()
# → ItemInstanceService._use_repair_kit()
# → ItemInstanceDAO.get_one() - получение целевого предмета для ремонта
target_item_id = kwargs.get('target_item_id')
if not target_item_id:
    return {"success": False, "message": "Не указан предмет для ремонта"}

target_item = await ItemInstanceDAO.get_one(session, target_item_id)
if not target_item or target_item.inventory_id != player.inventory_id:
    return {"success": False, "message": "Предмет не найден в инвентаре"}

# → ItemInstanceDAO.update_one() - увеличение зарядов целевого предмета
await ItemInstanceDAO.update_one(session, {
    'id': target_item_id,
    'uses': target_item.uses + 1
})

# → ItemInstanceDAO.use_item() - уменьшение uses ремонтного набора
await ItemInstanceDAO.use_item(session, item_instance.id)
```



---

### 16. Рука мидаса

**Описание**: Обмен предмета с колеса на 2 очка.

**Метод ItemInstanceService**: `_use_midas_hand()` - возвращает информацию об обмене предмета на очки, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_midas_hand()
wheel_item = kwargs.get('wheel_item')
if not wheel_item:
    return {"success": False, "message": "Не указан предмет с колеса"}

# Здесь должна быть логика добавления очков
# await PlayerStatsDAO.increment_stats(session, {"player_id": player.id, "total_points": 2})

await ItemInstanceDAO.use_item(session, item_instance.id)
return {"success": True, "message": f"Предмет '{wheel_item}' обменян на 2 очка", "points_gained": 2}
```

---

### 17. Реверсивные сапоги

**Описание**: Возврат назад на значение кубика.

**Метод ItemInstanceService**: `_use_reverse_boots()` - перемещает игрока назад на значение кубика, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_reverse_boots()
dice_value = kwargs.get('dice_value')
if not dice_value:
    return {"success": False, "message": "Не указано значение кубика"}

new_cell_id = max(0, player.cell_id - dice_value)
await self.player_service.update_player(player.id, {"cell_id": new_cell_id})
await ItemInstanceDAO.use_item(session, item_instance.id)
```



---

### 18. Парные кольца времени

**Описание**: Связывает двух игроков для совместного использования.

**Метод ItemInstanceService**: `_use_time_rings()` - создает копию кольца у целевого игрока, обновляет текущее кольцо

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_time_rings()
if not target_player:
    return {"success": False, "message": "Не указан целевой игрок"}

await InventoryDAO.add_item_to_inventory(session, {
    "inventory_id": target_player.inventory_id,
    "item_id": item_instance.item_id,
    "uses": item_instance.uses,
    "modifier_turns": None
})

await ItemInstanceDAO.update_one(session, {
    'id': item_instance.id,
    'modifier_turns': None
})
```



---

### 19. Четырехлистный клевер

**Описание**: Отбивание ловушек или бонусы на аукционах.

**Метод ItemInstanceService**: `_use_lucky_clover()` - в зависимости от типа использования отбивает ловушку или дает бонус на аукционе

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_lucky_clover()
use_type = kwargs.get('use_type')

if use_type == 'block_trap':
    trap_item_id = kwargs.get('trap_item_id')
    if not trap_item_id:
        return {"success": False, "message": "Не указана ловушка для отбивания"}
    
    await ItemInstanceDAO.delete_one(session, trap_item_id)
    await ItemInstanceDAO.use_item(session, item_instance.id)
    return {"success": True, "message": "Ловушка отбита"}

elif use_type == 'auction_bonus':
    bonus_type = kwargs.get('bonus_type')
    
    if bonus_type == 'points':
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "Получено +2 очка за прохождение игры"}
    
    elif bonus_type == 'easy_difficulty':
        await self.effects_service.add_player_effect(
            player_id=player.id,
            effect_name="easy_difficulty",
            effect_type=EffectType.BUFF,
            effect_category=EffectCategory.GAME_MODIFIER,
            turns_remaining=1,
            session=session
        )
        await ItemInstanceDAO.use_item(session, item_instance.id)
        return {"success": True, "message": "Игра будет пройдена на легком уровне сложности"}
```

---

### 20. Шоколад

**Описание**: Уменьшает время на клетке на 1 час.

**Метод ItemInstanceService**: `_use_chocolate()` - уменьшает время на клетке на 1 час, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_chocolate()
cell_id = kwargs.get('cell_id')
if not cell_id:
    return {"success": False, "message": "Не указана клетка для применения эффекта"}

cell = await self.cell_service.get_cell(cell_id)
if not cell:
    return {"success": False, "message": "Клетка не найдена"}

new_min_time = max(1, cell.min_time - 1)
new_max_time = max(new_min_time + 1, cell.max_time - 1)

await self.cell_service.update_cell(cell_id, {
    "min_time": new_min_time,
    "max_time": new_max_time
})

await ItemInstanceDAO.use_item(session, item_instance.id)
```



#### При получении предмета (on_acquire):
```python
# InventoryService.add_item_to_inventory()
# → InventoryDAO.add_item_to_inventory()
# → ItemInstanceDAO.create_one()
# → ItemInstanceService._on_acquire_chocolate()
# → InventoryDAO.search_items_in_inventory() - поиск всех шоколадов в инвентаре
items = await InventoryDAO.search_items_in_inventory(session, inventory_id)
chocolate_items = [item for item in items if item.item.title == "Шоколад"]
if len(chocolate_items) >= 4:
    total_uses = sum(item.uses for item in chocolate_items)
    # → ItemInstanceDAO.delete_one() - удаление всех 4 шоколадов
    for item in chocolate_items:
        await ItemInstanceDAO.delete_one(session, item.id)
    # → InventoryDAO.add_item_to_inventory() - создание плитки шоколада
    await InventoryDAO.add_item_to_inventory(session, {
        "inventory_id": inventory_id,
        "item_id": item_instance.item_id,
        "uses": 1,
        "modifier_turns": None
    })
    return {"success": True, "message": "4 шоколада превращены в плитку шоколада"}
```

---

### 21. Туалетка

**Описание**: Возврат на предыдущую клетку вместо тюрьмы.

**Метод ItemInstanceService**: `_use_toilet_paper()` - перемещает игрока на предыдущую клетку, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_toilet_paper()
previous_cell_id = kwargs.get('previous_cell_id')
if not previous_cell_id:
    return {"success": False, "message": "Не указана предыдущая клетка"}

await self.player_service.update_player(player.id, {"cell_id": previous_cell_id})
await ItemInstanceDAO.use_item(session, item_instance.id)
```

---

### 22. Дырявый парашют

**Описание**: Перемещение на старт, потеря 2 очков, следующая игра без очков.

**Метод ItemInstanceService**: `_use_parachute()` - перемещает игрока на старт, добавляет эффект "no_points_next_game" на 1 ход, затем использует предмет

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_parachute()
await self.player_service.update_player(player.id, {"cell_id": 0})

await self.effects_service.add_player_effect(
    player_id=player.id,
    effect_name="no_points_next_game",
    effect_type=EffectType.DEBUFF,
    effect_category=EffectCategory.GAME_MODIFIER,
    turns_remaining=1,
    session=session
)

await ItemInstanceDAO.use_item(session, item_instance.id)
```

---

### 23. Наперсток удачи

**Описание**: Замена неугодного пункта на нужный при кручении колеса.

**Метод ItemInstanceService**: `_use_lucky_thimble()` - возвращает информацию о замене предметов

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_lucky_thimble()
unwanted_item = kwargs.get('unwanted_item')
desired_item = kwargs.get('desired_item')

if not unwanted_item or not desired_item:
    return {"success": False, "message": "Не указаны предметы для замены"}

return {"success": True, "message": f"Пункт '{unwanted_item}' заменен на '{desired_item}'"}
```

---

### 24. Рука для fisting

**Описание**: Делает другого игрока рабом.

**Метод ItemInstanceService**: `_use_fisting_hand()` - создает копию руки у целевого игрока, обновляет текущую руку

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_fisting_hand()
if not target_player:
    return {"success": False, "message": "Не указан целевой игрок"}

await InventoryDAO.add_item_to_inventory(session, {
    "inventory_id": target_player.inventory_id,
    "item_id": item_instance.item_id,
    "uses": item_instance.uses,
    "modifier_turns": item_instance.modifier_turns
})

await ItemInstanceDAO.update_one(session, {
    'id': item_instance.id,
    'modifier_turns': item_instance.modifier_turns
})
```

---

### 25. Плюсовый блокнот

**Описание**: Бонусы при одинаковых значениях кубиков.

**Метод ItemInstanceService**: `_use_plus_notebook()` - проверяет одинаковые значения кубиков, возвращает соответствующие бонусы

**Логика работы**:

#### При использовании предмета:
```python
# ItemInstanceService._use_plus_notebook()
dice_values = kwargs.get('dice_values', [])

if len(dice_values) == 2 and dice_values[0] == dice_values[1]:
    if dice_values[0] == 6:
        return {"success": True, "message": "Выпали две шестерки! Получено +1 очко", "bonus_points": 1}
    else:
        return {"success": True, "message": f"Выпали одинаковые значения! +2 к движению", "movement_bonus": 2}

return {"success": True, "message": "Обычный бросок кубиков"}
```

---

## Специальные взаимодействия

### Уничтожение конфликтующих предметов

#### При проверке взаимодействий:
```python
# InventoryService.use_item()
# → ItemInstanceService._check_item_interactions()
# → InventoryDAO.search_items_in_inventory() - поиск всех предметов в инвентаре
items = await InventoryDAO.search_items_in_inventory(session, player.inventory_id)

# Читерский кубик + Кубик хуюбика
cheat_dice = None
huybik_dice = None

for item in items:
    if item.item.title == "Читерский кубик":
        cheat_dice = item
    elif item.item.title == "Кубик хуюбика":
        huybik_dice = item

if cheat_dice and huybik_dice:
    # → ItemInstanceDAO.delete_one() - удаление конфликтующих предметов
    await ItemInstanceDAO.delete_one(session, cheat_dice.id)
    await ItemInstanceDAO.delete_one(session, huybik_dice.id)
```



---

## Алгоритм обработки эффектов при завершении игры

### EffectsService.on_game_completed()

```python
# 1. Удаляем эффекты от использованных предметов
# → PlayerEffectsDAO.get_many() - получение всех активных эффектов игрока
effects = await PlayerEffectsDAO.get_many(session, {
    "player_id": player_id,
    "is_active": True
})

for effect in effects:
    if effect.item_instance_id:
        # → ItemInstanceDAO.get_one() - проверка существования экземпляра предмета
        item_instance = await ItemInstanceDAO.get_one(session, effect.item_instance_id)
        if not item_instance:  # ItemInstance не существует (был использован)
            # → PlayerEffectsDAO.delete_one() - удаление эффекта
            await PlayerEffectsDAO.delete_one(session, effect.id)

# 2. Уменьшаем ходы для временных эффектов
for effect in effects:
    if effect.turns_remaining is not None and effect.turns_remaining > 0:
        effect.turns_remaining -= 1
        if effect.turns_remaining <= 0:
            # → PlayerEffectsDAO.delete_one() - удаление истекшего эффекта
            await PlayerEffectsDAO.delete_one(session, effect.id)
        else:
            # → PlayerEffectsDAO.update_one() - обновление оставшихся ходов
            await PlayerEffectsDAO.update_one(session, {
                "id": effect.id,
                "turns_remaining": effect.turns_remaining
            })
```


